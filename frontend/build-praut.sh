#!/bin/bash
# Build for praut.cz/app/ deployment

# Build with /app/ base href
npx ng build --configuration=production --base-href /app/

echo "Build complete! Output in dist/frontend/browser/"
echo "Deploy to server and configure nginx with praut.cz.conf"
