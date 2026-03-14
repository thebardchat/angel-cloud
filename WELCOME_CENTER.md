# Welcome Center - Angel Cloud

**Professional 3D Welcome Experience with Contributor System**

---

## Overview

The Welcome Center is a professional, interactive interface for Angel Cloud / LogiBot system featuring:
- 3D digital avatar integration
- Real-time system metrics
- Contributor authentication and management
- Professional UI with Matrix-style animations

---

## Quick Start

### 1. Start Welcome Center

```bash
# Activate environment
source venv/bin/activate

# Run welcome center API
python3 welcome_center_api.py
```

Access at: http://localhost:8081

### 2. View Welcome Page

Open browser to `http://localhost:8081` to see:
- Shane's 3D digital avatar
- Live system metrics (drivers, models, uptime)
- System component status
- Contributor application form

---

## Features

### 3D Digital Avatar
- Located in `/3D Face/` directory
- 28 different avatar variations
- CRT-style scan line effects
- Real-time visualization

### Live System Metrics
- **Total Syncs**: Data sync operations
- **AI Queries**: Legacy AI interactions
- **Cost Savings**: Monthly cloud cost savings ($1,000/mo)
- **Contributors**: Active contributor count

### System Components Display
- Data Sync (Google Sheets → Firestore)
- Legacy AI (Custom trained models)
- 8TB Drive (Training storage)
- Multi-Computer Sync (Work ↔ Home)

---

## Contributor System

### Become a Contributor

#### Qualification Criteria

Contributors must meet ALL criteria:

1. **GitHub Stars**: Minimum 10 stars across all public repos
2. **Public Repositories**: At least 3 public repositories
3. **Verified Email**: Email address must be verified
4. **Admin Approval**: Manual approval by system admin

### Application Process

1. **Apply on Welcome Center**
   - Click "Apply as Contributor"
   - Fill out form with GitHub info
   - Submit application

2. **Automated Check**
   - System validates GitHub stats
   - Checks against criteria
   - Creates pending application

3. **Admin Approval**
   - Admin reviews application
   - Approves or rejects
   - Contributor receives token

4. **Start Contributing**
   - Login with credentials
   - Submit contributions
   - Track submission status

### Contribution Types

Contributors can submit:

**UI Enhancements**
- Welcome center improvements
- Dashboard redesigns
- Animation enhancements

**3D Models**
- Digital avatar variations
- Environment models
- Interactive elements

**Features**
- New system integrations
- API endpoints
- Monitoring tools

**Bug Fixes**
- UI bugs
- Performance improvements
- Browser compatibility

---

## API Reference

### Contributor Registration

```bash
POST /api/contributor/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "github_url": "https://github.com/johndoe",
  "github_stats": {
    "total_stars": 25,
    "public_repos": 5
  },
  "email_verified": true
}
```

**Response (Success):**
```json
{
  "success": true,
  "contributor_id": "abc123def456",
  "status": "pending_approval",
  "message": "Application submitted. Awaiting admin approval."
}
```

**Response (Failure):**
```json
{
  "success": false,
  "error": "Does not meet contributor criteria",
  "criteria": {
    "meets_criteria": false,
    "checks": {
      "github_stars": {
        "required": 10,
        "actual": 5,
        "passed": false
      }
    }
  }
}
```

### Contributor Login

```bash
POST /api/contributor/login
Content-Type: application/json

{
  "username": "johndoe"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "contributor_id": "abc123def456",
  "username": "johndoe"
}
```

### Submit Contribution

```bash
POST /api/contribution/submit
Authorization: Bearer <token>
Content-Type: application/json

{
  "type": "ui",
  "title": "Enhanced Matrix Animation",
  "description": "Improved matrix rain effect with customizable colors",
  "files": [
    "welcome_center/matrix-v2.js"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "contribution_id": "contrib789",
  "status": "review"
}
```

### Get Contribution Criteria

```bash
GET /api/contributor/criteria
```

**Response:**
```json
{
  "criteria": {
    "min_github_stars": 10,
    "min_repos": 3,
    "verified_email": true,
    "approved_by_admin": true
  },
  "description": {
    "min_github_stars": "Minimum total stars across all public repos",
    "min_repos": "Minimum number of public repositories",
    "verified_email": "Email must be verified",
    "approved_by_admin": "Manual approval required by admin"
  }
}
```

### List Approved Contributions

```bash
GET /api/contributions
```

**Response:**
```json
{
  "contributions": [
    {
      "contributor": "johndoe",
      "type": "ui",
      "title": "Enhanced Matrix Animation",
      "description": "Improved matrix rain effect",
      "submitted_at": "2026-01-03T12:00:00",
      "status": "approved"
    }
  ]
}
```

---

## Admin Functions

### Approve Contributor

```bash
POST /api/admin/approve/<contributor_id>
X-Admin-Key: your-admin-key

{}
```

**Response:**
```json
{
  "success": true,
  "message": "Contributor approved"
}
```

---

## File Structure

```
welcome_center/
├── index.html          # Main welcome page
├── styles.css          # Professional styling
└── welcome.js          # Interactive functionality

welcome_center_api.py   # Backend API
```

---

## Customization

### Change Admin Key

Edit `welcome_center_api.py`:

```python
# Line ~270
if auth_header != 'your-new-admin-key':
```

### Modify Contributor Criteria

Edit `CONTRIBUTOR_CRITERIA` dict in `welcome_center_api.py`:

```python
CONTRIBUTOR_CRITERIA = {
    'min_github_stars': 5,    # Lower requirement
    'min_repos': 1,            # Fewer repos required
    'verified_email': True,
    'approved_by_admin': True
}
```

### Add Custom Metrics

Edit `welcome.js` in `loadMetrics()` function:

```javascript
async function loadMetrics() {
    // Add your custom metric fetch
    const customMetric = await fetch('/api/your-metric');
    document.getElementById('custom-value').textContent = customMetric.value;
}
```

---

## Integration with Main System

### Health Check Integration

The welcome center checks `/health` endpoint:

```python
# In logibot_core.py or webhook_receiver.py
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })
```

### Metrics Integration

Welcome center can query:
- Firestore for driver counts
- Ollama API for model counts
- System logs for sync counts

```javascript
// In welcome.js
const driversResponse = await fetch('/api/drivers/count');
const driversData = await driversResponse.json();
document.getElementById('driver-count').textContent = driversData.count;
```

---

## Security

### JWT Token Security

Tokens expire after 30 days. Configure in `welcome_center_api.py`:

```python
payload = {
    'contributor_id': contributor_id,
    'exp': datetime.utcnow() + timedelta(days=30)  # Adjust here
}
```

### Admin Authentication

**CRITICAL**: Change default admin key in production:

```python
# In welcome_center_api.py, line ~270
if auth_header != os.getenv('ADMIN_KEY', 'your-secure-admin-key'):
    return jsonify({'error': 'Unauthorized'}), 403
```

### CORS Configuration

For production, configure CORS properly:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://yourdomain.com'])
```

---

## Deployment

### Development
```bash
python3 welcome_center_api.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8081 welcome_center_api:app
```

### Docker

Add to `docker-compose.yml`:

```yaml
services:
  welcome-center:
    build: .
    command: python3 welcome_center_api.py
    ports:
      - "8081:8081"
    volumes:
      - ./welcome_center:/app/welcome_center
      - ./3D Face:/app/3D Face
      - ./credentials.json:/app/credentials.json:ro
    environment:
      - WEBHOOK_PORT=8081
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name welcomecenter.angelcloud.local;

    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Troubleshooting

### Issue: Matrix background not showing
**Solution**: Ensure canvas is rendered properly

```javascript
// Check console for errors
console.log('Canvas dimensions:', canvas.width, canvas.height);
```

### Issue: Contributor registration fails
**Solution**: Check Firestore credentials

```bash
# Verify credentials
python3 -c "from config import config; print(config.validate())"
```

### Issue: JWT tokens not working
**Solution**: Verify SECRET_KEY is set

```python
# In .env file
JWT_SECRET=your-long-random-secret-key-here
```

### Issue: 3D Face images not loading
**Solution**: Check file paths

```bash
ls -la "3D Face/"
# Ensure shane-angel-cloud-avatar.png exists
```

---

## Contributing Guidelines

### For Contributors

1. **Code Style**
   - Use consistent indentation (2 spaces for HTML/CSS/JS)
   - Comment complex logic
   - Test on multiple browsers

2. **Submission Process**
   - Create feature branch
   - Test thoroughly
   - Submit via contributor API
   - Wait for review

3. **Best Practices**
   - Optimize images (compress PNGs)
   - Use semantic HTML
   - Write accessible code
   - Test responsive design

### For Reviewers

1. **Code Review**
   - Check for security issues
   - Verify functionality
   - Test on multiple devices
   - Ensure performance

2. **Approval Process**
   - Review contribution
   - Test integration
   - Approve via API
   - Merge to main

---

## Future Enhancements

- [ ] 3D model viewer (Three.js integration)
- [ ] Real-time chat for contributors
- [ ] Contribution leaderboard
- [ ] Automated screenshot testing
- [ ] Progressive Web App (PWA) support
- [ ] WebRTC for live collaboration
- [ ] OAuth integration (GitHub login)
- [ ] Automated testing pipeline

---

**Last Updated:** 2026-01-03
**Version:** 1.0
**Maintainer:** Shane Brazelton

**Mission:** Create a professional, contributor-friendly welcome experience for Angel Cloud.
