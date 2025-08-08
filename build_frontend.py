#!/usr/bin/env python3
"""
Build frontend script that installs Node.js and builds the Next.js app
"""
import os
import subprocess
import sys

def run_command(cmd, cwd=None):
    """Run a command and handle errors"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)
    return result.stdout

def main():
    print("Building frontend...")
    
    # Check if we're on Heroku
    if os.environ.get('DYNO'):
        print("Detected Heroku environment")
        
        # Install Node.js using apt (Heroku has apt available)
        print("Installing Node.js...")
        try:
            run_command("curl -fsSL https://deb.nodesource.com/setup_18.x | bash -")
            run_command("apt-get install -y nodejs")
        except:
            print("Failed to install Node.js via apt, trying alternative method...")
            # Try using the nodejs binary that might be available
            run_command("which node || (curl -L https://nodejs.org/dist/v18.19.0/node-v18.19.0-linux-x64.tar.xz | tar -xJ && mv node-v18.19.0-linux-x64 /tmp/node && ln -sf /tmp/node/bin/node /usr/local/bin/node && ln -sf /tmp/node/bin/npm /usr/local/bin/npm)")
    
    # Check if Node.js is available
    try:
        node_version = run_command("node --version")
        npm_version = run_command("npm --version")
        print(f"Node.js version: {node_version.strip()}")
        print(f"npm version: {npm_version.strip()}")
    except:
        print("Node.js not found, skipping frontend build")
        print("Frontend will be built by heroku-postbuild during Node.js buildpack phase")
        return
    
    # Change to frontend directory
    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        print(f"Frontend directory not found: {frontend_dir}")
        sys.exit(1)
    
    print(f"Changing to directory: {frontend_dir}")
    
    # Install dependencies
    if os.path.exists(os.path.join(frontend_dir, "package-lock.json")):
        print("Installing dependencies with npm ci...")
        run_command("npm ci", cwd=frontend_dir)
    else:
        print("Installing dependencies with npm install...")
        run_command("npm install", cwd=frontend_dir)
    
    # Build the frontend
    print("Building Next.js application...")
    run_command("npm run build", cwd=frontend_dir)
    
    # Check if build was successful
    dist_dir = os.path.join(frontend_dir, "dist")
    index_file = os.path.join(dist_dir, "index.html")
    
    if os.path.exists(index_file):
        print("✅ Frontend build successful - index.html found")
        # List contents of dist directory
        if os.path.exists(dist_dir):
            print("Contents of dist directory:")
            for item in os.listdir(dist_dir):
                print(f"  - {item}")
    else:
        print("❌ Frontend build failed - index.html not found")
        if os.path.exists(dist_dir):
            print("Contents of dist directory:")
            for item in os.listdir(dist_dir):
                print(f"  - {item}")
        else:
            print("dist directory does not exist")
        sys.exit(1)

if __name__ == "__main__":
    main()