# Conference Seeker

A tool to track academic conferences and automatically find new editions or similar conferences.

## Features

- Track academic conferences with their details
- Automatic web search for new editions
- Similarity-based matching using language models
- Email notifications for promising matches
- Modern GUI for easy management
- Cloud-based deployment with Azure

## Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/confseeker.git
cd confseeker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
NOTIFICATION_EMAIL=your-email@gmail.com
SIMILARITY_THRESHOLD=0.7
```

5. Start the API server:
```bash
python app.py
```

6. Start the GUI:
```bash
python gui.py
```

## Azure Deployment

1. Install Azure CLI:
   - Download and install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
   - Log in to Azure:
   ```bash
   az login
   ```

2. Create an Azure SQL Database:
   ```bash
   az sql server create --name confseeker-sql --resource-group confseeker-rg --location westeurope --admin-user confseekeradmin --admin-password <your-password>
   az sql db create --resource-group confseeker-rg --server confseeker-sql --name confseekerdb
   ```

3. Get the connection string:
   ```bash
   az sql db show-connection-string --client sqlcmd --server confseeker-sql --database confseekerdb
   ```

4. Set up environment variables in Azure:
   ```bash
   az webapp config appsettings set --name confseeker-api --resource-group confseeker-rg --settings \
     DATABASE_URL="<your-sql-connection-string>" \
     SMTP_SERVER="smtp.gmail.com" \
     SMTP_PORT="587" \
     SMTP_USERNAME="your-email@gmail.com" \
     SMTP_PASSWORD="your-app-specific-password" \
     NOTIFICATION_EMAIL="your-email@gmail.com" \
     SIMILARITY_THRESHOLD="0.7"
   ```

5. Deploy the application:
   ```bash
   az webapp up --name confseeker-api --resource-group confseeker-rg --runtime python:3.9
   ```

6. Set up Azure Scheduler:
   - Go to Azure Portal
   - Create a new Scheduler job collection
   - Add a new job to run daily:
     - Action type: HTTP
     - URL: https://confseeker-api.azurewebsites.net/api/check
     - Method: POST
     - Schedule: Daily

## Usage

1. Add Conferences:
   - Click "Add Conference"
   - Fill in the conference details
   - Click "Save"

2. Manage Conferences:
   - View all conferences in the list
   - Edit or delete conferences using the buttons
   - Filter conferences using the search box
   - Sort by clicking column headers

3. Check for Updates:
   - Click "Check Now" to manually check for updates
   - View results in the preview section
   - Receive email notifications for matches

4. View Results:
   - Results are shown in the preview section
   - Each result shows similarity score and link
   - Click links to visit conference websites

## Configuration

Edit the `.env` file to configure:
- Email notification settings
- Similarity threshold for matching
- Search interval

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.