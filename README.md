# Simple EHR Blockchain System

A simplified Electronic Health Records (EHR) system built with blockchain technology using Python and Streamlit.

## Features

- **Blockchain Implementation**: Secure, tamper-proof medical records storage
- **Patient Management**: Add and view patient medical records
- **Search Functionality**: Find records by patient ID
- **Data Integrity**: SHA-256 hashing ensures data cannot be modified
- **Web Interface**: User-friendly Streamlit dashboard
- **Export Options**: Download records as CSV

## Quick Start

### Local Development

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. Push these files to your GitHub repository:
   - `app.py`
   - `requirements.txt`
   - `README.md`

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub repository
4. Deploy!

## How It Works

### Blockchain Structure
- Each medical record is stored in a block
- Blocks are linked using cryptographic hashes
- Any tampering with records would break the chain
- Genesis block initializes the blockchain

### Medical Records
Records include:
- Patient ID and Name
- Age and Doctor information
- Diagnosis and Treatment details
- Timestamp and Block hash for verification

## Usage

1. **Add Records**: Use the "Add Medical Record" page to input new patient data
2. **View All**: See all records stored in the blockchain
3. **Search**: Find specific patient records by ID
4. **Verify**: Check blockchain integrity on the info page

## File Structure

```
simple-ehr-blockchain/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Security Features

- **Immutable Records**: Once added, records cannot be changed
- **Hash Verification**: Each block is cryptographically secured
- **Chain Validation**: System can verify entire blockchain integrity
- **Timestamp Tracking**: All records include creation timestamps

## Deployment Notes

- The application stores data in memory during the session
- For production use, consider adding persistent storage
- All patient data should be handled according to HIPAA guidelines
- This is a simplified educational example

## License

Open source - feel free to modify and improve
