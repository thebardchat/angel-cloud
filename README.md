# Angel Cloud

Mental wellness communication platform named after Angel Brazelton. Part of the [ShaneBrain ecosystem](https://github.com/thebardchat/shanebrain-core).

## Structure

```
angel-cloud/
├── angel_cloud_server.js    # Express API (port 5000) - users, auth, messaging, AI sentiment
├── models/                  # Mongoose schemas (User, Angel, Message)
├── routes/                  # API routes (auth, users, messaging, angels, AI)
├── services/                # Sentiment analysis, angel matching, notifications
├── middleware/               # JWT auth middleware
├── automation/               # Memory auto-save system
├── auth-bridge/              # SSO + security bridge (port 3005)
│   ├── angel-auth-bridge.js  # JWT auth, Pulsar wallet verification, encrypted vaults
│   ├── angel_chat_v2.js      # ShaneBrain Legacy AI chatbot (Gemini)
│   ├── dispatch_calculator_service.js  # AI dispatch time windows
│   └── logistics_api/        # Flask haul rate quoting API (port 5001)
├── welcome/                  # 3D Welcome Center (Three.js, registration flow)
│   ├── index.html            # Interactive 3D welcome page
│   └── shanebrain-avatar.glb # 3D avatar model
├── 3D Face/                  # CRT-style digital avatar interface
├── google_sheets_sync.py     # SRM Dispatch data sync to Firestore
└── life_command_center_sync.py  # Personal finance/family sync
```

## Angel Progression System

New Born -> Young Angel -> Growing Angel -> Helping Angel -> Guardian Angel -> Angel

## Related Repos

- [shanebrain-core](https://github.com/thebardchat/shanebrain-core) - Main AI brain
- [pulsar_sentinel](https://github.com/thebardchat/pulsar_sentinel) - Security layer
