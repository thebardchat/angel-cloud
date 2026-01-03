#!/usr/bin/env python3
"""
Welcome Center Backend API
Manages contributors, authentication, and welcome center content.
"""

from flask import Flask, request, jsonify, render_template_string, send_from_directory
from datetime import datetime, timedelta
import jwt
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

import firebase_admin
from firebase_admin import credentials, firestore

from config import config
from logger import LogiLogger

app = Flask(__name__)
app.config['SECRET_KEY'] = config.JWT_SECRET if hasattr(config, 'JWT_SECRET') else 'your-secret-key-change-this'

logger = LogiLogger.get_logger("welcome_center")

# Contributor criteria
CONTRIBUTOR_CRITERIA = {
    'min_github_stars': 10,
    'min_repos': 3,
    'verified_email': True,
    'approved_by_admin': True
}


class ContributorManager:
    """Manage contributors to the welcome center"""

    def __init__(self):
        self.db = None
        self.contributors_collection = config.get_public_collection("contributors")

    def initialize(self):
        """Initialize Firestore"""
        if not firebase_admin._apps:
            cred = credentials.Certificate(config.CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def check_criteria(self, contributor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if contributor meets criteria"""
        results = {
            'meets_criteria': True,
            'checks': {}
        }

        # Check GitHub stars
        total_stars = contributor_data.get('github_stats', {}).get('total_stars', 0)
        results['checks']['github_stars'] = {
            'required': CONTRIBUTOR_CRITERIA['min_github_stars'],
            'actual': total_stars,
            'passed': total_stars >= CONTRIBUTOR_CRITERIA['min_github_stars']
        }

        # Check number of repos
        repo_count = contributor_data.get('github_stats', {}).get('public_repos', 0)
        results['checks']['repo_count'] = {
            'required': CONTRIBUTOR_CRITERIA['min_repos'],
            'actual': repo_count,
            'passed': repo_count >= CONTRIBUTOR_CRITERIA['min_repos']
        }

        # Check verified email
        email_verified = contributor_data.get('email_verified', False)
        results['checks']['email_verified'] = {
            'required': True,
            'actual': email_verified,
            'passed': email_verified
        }

        # Overall pass/fail
        results['meets_criteria'] = all(
            check['passed'] for check in results['checks'].values()
        )

        return results

    def register_contributor(self, contributor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new contributor"""
        # Check criteria
        criteria_result = self.check_criteria(contributor_data)

        if not criteria_result['meets_criteria']:
            return {
                'success': False,
                'error': 'Does not meet contributor criteria',
                'criteria': criteria_result
            }

        # Create contributor record
        contributor = {
            'username': contributor_data['username'],
            'email': contributor_data['email'],
            'github_url': contributor_data.get('github_url', ''),
            'github_stats': contributor_data.get('github_stats', {}),
            'registered_at': datetime.utcnow().isoformat(),
            'approved': False,  # Requires admin approval
            'contributions': [],
            'status': 'pending'
        }

        # Save to Firestore
        doc_id = hashlib.sha256(contributor['username'].encode()).hexdigest()[:16]
        self.db.collection(self.contributors_collection).document(doc_id).set(contributor)

        logger.info(f"New contributor registered: {contributor['username']}")

        return {
            'success': True,
            'contributor_id': doc_id,
            'status': 'pending_approval',
            'message': 'Application submitted. Awaiting admin approval.'
        }

    def approve_contributor(self, contributor_id: str) -> bool:
        """Approve a contributor (admin only)"""
        doc_ref = self.db.collection(self.contributors_collection).document(contributor_id)
        doc_ref.update({
            'approved': True,
            'status': 'active',
            'approved_at': datetime.utcnow().isoformat()
        })

        logger.info(f"Contributor approved: {contributor_id}")
        return True

    def get_contributor(self, contributor_id: str) -> Optional[Dict[str, Any]]:
        """Get contributor by ID"""
        doc = self.db.collection(self.contributors_collection).document(contributor_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def submit_contribution(self, contributor_id: str, contribution: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a contribution"""
        contributor = self.get_contributor(contributor_id)

        if not contributor:
            return {'success': False, 'error': 'Contributor not found'}

        if not contributor.get('approved'):
            return {'success': False, 'error': 'Contributor not approved'}

        # Add contribution
        contribution_record = {
            'type': contribution['type'],  # 'ui', '3d_model', 'feature', 'bug_fix'
            'title': contribution['title'],
            'description': contribution['description'],
            'files': contribution.get('files', []),
            'submitted_at': datetime.utcnow().isoformat(),
            'status': 'review',
            'reviewed': False
        }

        # Update contributor document
        doc_ref = self.db.collection(self.contributors_collection).document(contributor_id)
        doc_ref.update({
            'contributions': firestore.ArrayUnion([contribution_record])
        })

        logger.info(f"Contribution submitted: {contribution['title']} by {contributor_id}")

        return {
            'success': True,
            'contribution_id': hashlib.sha256(contribution['title'].encode()).hexdigest()[:8],
            'status': 'review'
        }


# Initialize contributor manager
contributor_manager = ContributorManager()


def generate_token(contributor_id: str) -> str:
    """Generate JWT token for contributor"""
    payload = {
        'contributor_id': contributor_id,
        'exp': datetime.utcnow() + timedelta(days=30)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return contributor_id"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['contributor_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# API Routes

@app.route('/')
def index():
    """Welcome center homepage"""
    return send_from_directory('../welcome_center', 'index.html')


@app.route('/api/contributor/register', methods=['POST'])
def register():
    """Register as a contributor"""
    data = request.json

    required_fields = ['username', 'email', 'github_url']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    result = contributor_manager.register_contributor(data)

    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/contributor/login', methods=['POST'])
def login():
    """Login as contributor (simplified - would use OAuth in production)"""
    data = request.json
    username = data.get('username')

    # In production, verify credentials properly
    # For now, simplified lookup
    docs = contributor_manager.db.collection(contributor_manager.contributors_collection).where(
        'username', '==', username
    ).limit(1).stream()

    for doc in docs:
        contributor_data = doc.to_dict()

        if not contributor_data.get('approved'):
            return jsonify({'error': 'Not approved yet'}), 403

        token = generate_token(doc.id)
        return jsonify({
            'token': token,
            'contributor_id': doc.id,
            'username': contributor_data['username']
        }), 200

    return jsonify({'error': 'Contributor not found'}), 404


@app.route('/api/contribution/submit', methods=['POST'])
def submit_contribution():
    """Submit a contribution (requires authentication)"""
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401

    token = auth_header.split(' ')[1]
    contributor_id = verify_token(token)

    if not contributor_id:
        return jsonify({'error': 'Invalid token'}), 401

    contribution_data = request.json
    result = contributor_manager.submit_contribution(contributor_id, contribution_data)

    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400


@app.route('/api/contributions', methods=['GET'])
def list_contributions():
    """List all approved contributions"""
    # Fetch from Firestore
    contributors = contributor_manager.db.collection(contributor_manager.contributors_collection).where(
        'approved', '==', True
    ).stream()

    all_contributions = []

    for doc in contributors:
        data = doc.to_dict()
        for contrib in data.get('contributions', []):
            if contrib.get('status') == 'approved':
                all_contributions.append({
                    'contributor': data['username'],
                    **contrib
                })

    return jsonify({'contributions': all_contributions}), 200


@app.route('/api/contributor/criteria', methods=['GET'])
def get_criteria():
    """Get contributor criteria"""
    return jsonify({
        'criteria': CONTRIBUTOR_CRITERIA,
        'description': {
            'min_github_stars': 'Minimum total stars across all public repos',
            'min_repos': 'Minimum number of public repositories',
            'verified_email': 'Email must be verified',
            'approved_by_admin': 'Manual approval required by admin'
        }
    }), 200


@app.route('/api/admin/approve/<contributor_id>', methods=['POST'])
def approve_contributor_endpoint(contributor_id):
    """Approve a contributor (admin only)"""
    # In production, add admin authentication
    auth_header = request.headers.get('X-Admin-Key')

    if auth_header != 'your-admin-key':  # Replace with proper auth
        return jsonify({'error': 'Unauthorized'}), 403

    contributor_manager.approve_contributor(contributor_id)

    return jsonify({'success': True, 'message': 'Contributor approved'}), 200


def main():
    """Run welcome center API"""
    logger.info("Starting Welcome Center API")

    contributor_manager.initialize()

    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=config.WEBHOOK_PORT + 1 if hasattr(config, 'WEBHOOK_PORT') else 8081,
        debug=(config.ENVIRONMENT == 'development')
    )


if __name__ == "__main__":
    main()
