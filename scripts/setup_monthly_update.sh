#!/bin/bash
# Setup script for monthly automatic stock data updates
# This script helps configure a cron job to run monthly updates

echo "=========================================="
echo "Stock Analysis - Monthly Update Setup"
echo "=========================================="
echo ""

# Get the absolute path to the project
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONDA_ENV="stock_analysis"

echo "Project directory: $PROJECT_DIR"
echo "Conda environment: $CONDA_ENV"
echo ""

# Create the update script that cron will run
cat > "$PROJECT_DIR/scripts/monthly_update.sh" << 'EOF'
#!/bin/bash
# Monthly stock data update script
# This script is called by cron to update stock data

# Get project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Activate conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate stock_analysis

# Update daily data
echo "=========================================="
echo "Stock Data Monthly Update - $(date)"
echo "=========================================="
echo ""

echo "Updating daily data..."
python scripts/update_data.py --type daily

echo ""
echo "Updating hourly data..."
python scripts/update_data.py --type hourly --interval 1h

echo ""
echo "Update complete - $(date)"
echo "=========================================="
EOF

chmod +x "$PROJECT_DIR/scripts/monthly_update.sh"

echo "✓ Created monthly_update.sh script"
echo ""

# Show cron job instructions
echo "=========================================="
echo "Cron Job Setup Instructions"
echo "=========================================="
echo ""
echo "To schedule automatic monthly updates on the 26th at 6:00 PM:"
echo ""
echo "1. Edit your crontab:"
echo "   crontab -e"
echo ""
echo "2. Add this line:"
echo "   0 18 26 * * $PROJECT_DIR/scripts/monthly_update.sh >> $PROJECT_DIR/logs/monthly_update.log 2>&1"
echo ""
echo "   This runs on the 26th of every month at 6:00 PM"
echo ""
echo "Alternative schedules:"
echo "   - Every day at 6 PM:        0 18 * * * ..."
echo "   - Every Monday at 6 PM:     0 18 * * 1 ..."
echo "   - 1st of each month 6 PM:   0 18 1 * * ..."
echo ""
echo "3. Save and exit"
echo ""
echo "To verify cron job is set:"
echo "   crontab -l"
echo ""
echo "=========================================="
echo ""

echo "Would you like to add the cron job now? (y/n)"
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    # Add cron job
    CRON_LINE="0 18 26 * * $PROJECT_DIR/scripts/monthly_update.sh >> $PROJECT_DIR/logs/monthly_update.log 2>&1"

    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "monthly_update.sh"; then
        echo "⚠ Cron job already exists. Skipping."
    else
        (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
        echo "✓ Cron job added successfully!"
        echo ""
        echo "Current cron jobs:"
        crontab -l | grep "monthly_update"
    fi
else
    echo "Skipped cron job setup. You can add it manually later."
fi

echo ""
echo "Setup complete!"
