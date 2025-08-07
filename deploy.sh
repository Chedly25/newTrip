#!/bin/bash

# Wanderlog AI Deployment Script
# Supports Railway, Render, Heroku, and DigitalOcean

set -e

PLATFORM=${1:-railway}
APP_NAME=${2:-wanderlog-ai}

echo "🚀 Deploying Wanderlog AI to $PLATFORM..."

# Check if required environment variables are set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY environment variable is required"
    echo "Please set it with: export ANTHROPIC_API_KEY=your-key"
    exit 1
fi

case $PLATFORM in
    railway)
        echo "📡 Deploying to Railway.app..."
        
        # Check if Railway CLI is installed
        if ! command -v railway &> /dev/null; then
            echo "Installing Railway CLI..."
            npm install -g @railway/cli
        fi
        
        # Login to Railway
        echo "Please login to Railway:"
        railway login
        
        # Initialize project
        railway init $APP_NAME
        
        # Add services
        echo "Adding PostgreSQL and Redis..."
        railway add postgresql
        railway add redis
        
        # Set environment variables
        railway variables set ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
        railway variables set DEBUG=False
        railway variables set ENVIRONMENT=production
        
        # Deploy
        echo "Deploying application..."
        railway up
        
        echo "✅ Deployed to Railway! Check your dashboard for the URL."
        ;;
        
    heroku)
        echo "🔨 Deploying to Heroku..."
        
        # Check if Heroku CLI is installed
        if ! command -v heroku &> /dev/null; then
            echo "❌ Please install Heroku CLI first"
            exit 1
        fi
        
        # Create app
        heroku create $APP_NAME
        
        # Add buildpacks
        heroku buildpacks:add heroku/python -a $APP_NAME
        
        # Add add-ons
        heroku addons:create heroku-postgresql:mini -a $APP_NAME
        heroku addons:create heroku-redis:mini -a $APP_NAME
        
        # Set environment variables
        heroku config:set ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY -a $APP_NAME
        heroku config:set DEBUG=False -a $APP_NAME
        heroku config:set ENVIRONMENT=production -a $APP_NAME
        
        # Create Procfile
        echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > backend/Procfile
        echo "worker: celery -A app.workers.celery_app worker --loglevel=info" >> backend/Procfile
        
        # Deploy
        cd backend
        git init
        git add .
        git commit -m "Initial deployment"
        git remote add heroku https://git.heroku.com/$APP_NAME.git
        git push heroku main
        
        echo "✅ Deployed to Heroku! URL: https://$APP_NAME.herokuapp.com"
        ;;
        
    render)
        echo "🎨 Setting up for Render deployment..."
        
        # Create render.yaml
        cat > render.yaml << EOF
services:
  - type: web
    name: $APP_NAME-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port \$PORT
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: $APP_NAME-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: $APP_NAME-redis
          type: redis
          property: connectionString
      - key: ANTHROPIC_API_KEY
        value: $ANTHROPIC_API_KEY
      - key: DEBUG
        value: False
      - key: ENVIRONMENT
        value: production

databases:
  - name: $APP_NAME-db
    plan: free
    databaseName: wanderlog
    user: wanderlog

services:
  - type: redis
    name: $APP_NAME-redis
    plan: free
EOF
        
        echo "✅ render.yaml created! Now:"
        echo "1. Push your code to GitHub"
        echo "2. Connect your repo to Render"
        echo "3. Render will auto-deploy using render.yaml"
        ;;
        
    digitalocean)
        echo "🌊 Setting up for DigitalOcean App Platform..."
        
        # Create app.yaml
        cat > app.yaml << EOF
name: $APP_NAME
services:
- environment_slug: python
  github:
    branch: main
    deploy_on_push: true
    repo: your-username/$APP_NAME
  name: api
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  source_dir: backend
  envs:
  - key: DATABASE_URL
    scope: RUN_TIME
    value: \${db.DATABASE_URL}
  - key: REDIS_URL
    scope: RUN_TIME
    value: \${redis.REDIS_URL}
  - key: ANTHROPIC_API_KEY
    scope: RUN_TIME
    value: $ANTHROPIC_API_KEY
  - key: DEBUG
    scope: RUN_TIME
    value: False
databases:
- engine: PG
  name: db
  version: "15"
- engine: REDIS
  name: redis
  version: "7"
EOF
        
        echo "✅ app.yaml created! Now:"
        echo "1. Push your code to GitHub"
        echo "2. Create app on DigitalOcean App Platform"
        echo "3. Use the app.yaml configuration"
        ;;
        
    *)
        echo "❌ Unsupported platform: $PLATFORM"
        echo "Supported platforms: railway, heroku, render, digitalocean"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment setup complete!"
echo ""
echo "📚 Next steps:"
echo "1. Set up your domain name (optional)"
echo "2. Configure SSL/HTTPS"
echo "3. Set up monitoring and alerts"
echo "4. Test your deployed application"
echo ""
echo "📖 For detailed documentation, see: README.md"