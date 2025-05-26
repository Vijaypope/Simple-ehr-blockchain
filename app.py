import streamlit as st
import hashlib
import json
import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import pickle

# Configure Streamlit page
st.set_page_config(
    page_title="EHR Blockchain System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for animations and styling
st.markdown("""
<style>
    /* Main theme */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Animated header */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animated-header {
        animation: fadeInDown 1s ease-out;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: bold;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    /* Pulse animation for important elements */
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .record-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .record-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 20px rgba(0,0,0,0.15);
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    
    /* Block styling */
    .blockchain-block {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
    }
    
    .genesis-block {
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
        border-left: 4px solid #FF6B6B;
    }
    
    /* Loading animation */
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-spinner {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 2rem auto;
    }
    
    /* Security features */
    .security-badge {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# SQLite Database Functions
def init_database():
    """Initialize SQLite database for blockchain storage"""
    conn = sqlite3.connect('ehr_blockchain.db')
    c = conn.cursor()
    
    # Create table for blockchain data
    c.execute('''CREATE TABLE IF NOT EXISTS blockchain_data
                 (id INTEGER PRIMARY KEY,
                  blockchain_state BLOB,
                  timestamp DATETIME,
                  created_date DATE)''')
    
    # Create table for individual medical records (for easier querying)
    c.execute('''CREATE TABLE IF NOT EXISTS medical_records
                 (id INTEGER PRIMARY KEY,
                  patient_id TEXT,
                  patient_name TEXT,
                  age INTEGER,
                  gender TEXT,
                  diagnosis TEXT,
                  treatment TEXT,
                  doctor TEXT,
                  hospital TEXT,
                  severity TEXT,
                  block_index INTEGER,
                  block_hash TEXT,
                  timestamp DATETIME,
                  created_date DATE)''')
    
    conn.commit()
    conn.close()

def save_blockchain_to_db(blockchain):
    """Save the entire blockchain state to database"""
    conn = sqlite3.connect('ehr_blockchain.db')
    c = conn.cursor()
    
    # Serialize the blockchain object
    blockchain_data = pickle.dumps(blockchain)
    current_time = datetime.datetime.now()
    current_date = datetime.date.today()
    
    # Insert new blockchain state
    c.execute("INSERT INTO blockchain_data (blockchain_state, timestamp, created_date) VALUES (?, ?, ?)",
              (blockchain_data, current_time, current_date))
    
    conn.commit()
    conn.close()

def load_blockchain_from_db():
    """Load the most recent blockchain state from database"""
    conn = sqlite3.connect('ehr_blockchain.db')
    c = conn.cursor()
    
    # Get the most recent blockchain state
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    c.execute("SELECT blockchain_state FROM blockchain_data WHERE created_date > ? ORDER BY timestamp DESC LIMIT 1", (week_ago,))
    result = c.fetchone()
    
    conn.close()
    
    if result:
        return pickle.loads(result[0])
    else:
        return None

def save_medical_record_to_db(record_data, block_index, block_hash):
    """Save individual medical record to database for easy querying"""
    conn = sqlite3.connect('ehr_blockchain.db')
    c = conn.cursor()
    
    current_time = datetime.datetime.now()
    current_date = datetime.date.today()
    
    c.execute("""INSERT INTO medical_records 
                 (patient_id, patient_name, age, gender, diagnosis, treatment, 
                  doctor, hospital, severity, block_index, block_hash, timestamp, created_date)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (record_data['patient_id'], record_data['patient_name'], record_data['age'],
               record_data['gender'], record_data['diagnosis'], record_data['treatment'],
               record_data['doctor'], record_data['hospital'], record_data['severity'],
               block_index, block_hash, current_time, current_date))
    
    conn.commit()
    conn.close()

def cleanup_old_data():
    """Remove data older than 7 days"""
    conn = sqlite3.connect('ehr_blockchain.db')
    c = conn.cursor()
    
    week_ago = datetime.date.today() - datetime.timedelta(days=7)
    
    # Clean up old blockchain states (keep only the most recent one within the week)
    c.execute("DELETE FROM blockchain_data WHERE created_date < ?", (week_ago,))
    
    # Clean up old medical records
    c.execute("DELETE FROM medical_records WHERE created_date < ?", (week_ago,))
    
    conn.commit()
    conn.close()

def get_database_stats():
    """Get statistics about the database"""
    conn = sqlite3.connect('ehr_blockchain.db')
    c = conn.cursor()
    
    # Get record count
    c.execute("SELECT COUNT(*) FROM medical_records")
    record_count = c.fetchone()[0]
    
    # Get blockchain states count
    c.execute("SELECT COUNT(*) FROM blockchain_data")
    blockchain_states = c.fetchone()[0]
    
    # Get oldest record date
    c.execute("SELECT MIN(created_date) FROM medical_records")
    oldest_record = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_records_in_db': record_count,
        'blockchain_states': blockchain_states,
        'oldest_record_date': oldest_record
    }

@dataclass
class MedicalRecord:
    """Enhanced medical record structure"""
    patient_id: str
    patient_name: str
    age: int
    gender: str
    diagnosis: str
    treatment: str
    doctor: str
    hospital: str
    severity: str
    timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

class Block:
    """Enhanced blockchain block with additional metadata"""
    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = self.mine_block()
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 2) -> int:
        """Simple proof of work mining"""
        nonce = 0
        while True:
            temp_hash = hashlib.sha256(f"{self.index}{self.timestamp}{json.dumps(self.data)}{self.previous_hash}{nonce}".encode()).hexdigest()
            if temp_hash[:difficulty] == "0" * difficulty:
                return nonce
            nonce += 1
            if nonce > 1000:  # Prevent infinite loop in demo
                return nonce
    
    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "nonce": self.nonce
        }

class EnhancedEHRBlockchain:
    """Enhanced EHR Blockchain with mining and advanced features"""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.difficulty = 2
        self.mining_reward = 10
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            timestamp=str(datetime.datetime.now()),
            data={"message": "Genesis Block - EHR Blockchain Initialized", "type": "genesis"},
            previous_hash="0"
        )
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_medical_record(self, record: MedicalRecord) -> bool:
        """Add a new medical record to the blockchain with mining animation"""
        try:
            # Show mining process
            mining_placeholder = st.empty()
            mining_placeholder.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)
            time.sleep(1)  # Simulate mining time
            
            new_block = Block(
                index=len(self.chain),
                timestamp=str(datetime.datetime.now()),
                data=record.to_dict(),
                previous_hash=self.get_latest_block().hash
            )
            self.chain.append(new_block)
            
            # Save to database
            save_medical_record_to_db(record.to_dict(), new_block.index, new_block.hash)
            save_blockchain_to_db(self)
            
            mining_placeholder.empty()
            return True
        except Exception as e:
            st.error(f"Error adding record: {str(e)}")
            return False
    
    def get_all_records(self) -> List[Dict]:
        """Get all medical records from the blockchain"""
        records = []
        for block in self.chain[1:]:  # Skip genesis block
            if isinstance(block.data, dict) and "patient_name" in block.data:
                record_with_block_info = block.data.copy()
                record_with_block_info["block_index"] = block.index
                record_with_block_info["block_hash"] = block.hash
                records.append(record_with_block_info)
        return records
    
    def get_patient_records(self, patient_id: str) -> List[Dict]:
        """Get all records for a specific patient"""
        all_records = self.get_all_records()
        return [record for record in all_records if record.get("patient_id") == patient_id]
    
    def get_statistics(self) -> Dict:
        """Get blockchain statistics"""
        records = self.get_all_records()
        if not records:
            return {"total_patients": 0, "total_records": 0, "hospitals": [], "doctors": []}
        
        df = pd.DataFrame(records)
        return {
            "total_patients": df['patient_id'].nunique(),
            "total_records": len(records),
            "hospitals": df['hospital'].unique().tolist(),
            "doctors": df['doctor'].unique().tolist(),
            "avg_age": df['age'].mean(),
            "severity_distribution": df['severity'].value_counts().to_dict()
        }
    
    def validate_chain(self) -> bool:
        """Validate the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True

# Initialize database and blockchain in session state
if 'db_initialized' not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

if 'blockchain' not in st.session_state:
    # Try to load blockchain from database first
    loaded_blockchain = load_blockchain_from_db()
    if loaded_blockchain:
        st.session_state.blockchain = loaded_blockchain
        st.session_state.loaded_from_db = True
    else:
        st.session_state.blockchain = EnhancedEHRBlockchain()
        st.session_state.loaded_from_db = False

def main():
    # Animated header
    st.markdown('<h1 class="animated-header">🏥 EHR Blockchain System</h1>', unsafe_allow_html=True)
    
    # Show database status
    if st.session_state.get('loaded_from_db', False):
        st.success("🗄 Data loaded from database - your records are persistent!")
    
    # Sidebar navigation with icons
    st.sidebar.markdown("### 🚀 Navigation")
    pages = {
        "🏠 Dashboard": "Dashboard",
        "📝 Add Record": "Add Record", 
        "🔍 Patient Records": "Patient Records",
        "⛓ Blockchain Explorer": "Blockchain Explorer",
        "🔐 Security Audit": "Security Audit",
        "🗄 Database Management": "Database Management"
    }
    
    selected_page = st.sidebar.selectbox("Choose a page:", list(pages.keys()))
    page = pages[selected_page]
    
    # Blockchain info in sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⛓ Blockchain Info")
    st.sidebar.metric("Blocks", len(st.session_state.blockchain.chain))
    st.sidebar.metric("Records", len(st.session_state.blockchain.get_all_records()))
    
    is_valid = st.session_state.blockchain.validate_chain()
    status_color = "🟢" if is_valid else "🔴"
    st.sidebar.markdown(f"**Status:** {status_color} {'Valid' if is_valid else 'Invalid'}")
    
    # Page routing
    if page == "Dashboard":
        dashboard_page()
    elif page == "Add Record":
        add_record_page()
    elif page == "Patient Records":
        patient_records_page()
    elif page == "Blockchain Explorer":
        blockchain_explorer_page()
    elif page == "Security Audit":
        security_audit_page()
    elif page == "Database Management":
        database_management_page()

def security_audit_page():
    """New security audit page"""
    st.markdown("## 🔐 Security Audit")
    
    blockchain = st.session_state.blockchain
    
    # Validate blockchain
    is_valid = blockchain.validate_chain()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if is_valid:
            st.success("✅ Blockchain Integrity: VALID")
        else:
            st.error("❌ Blockchain Integrity: COMPROMISED")
    
    with col2:
        st.info(f"🔗 Total Blocks: {len(blockchain.chain)}")
    
    # Security metrics
    st.markdown("### 🛡 Security Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🔒 Encryption</h3>
            <p>SHA-256 Hashing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⛏ Difficulty</h3>
            <p>Level {blockchain.difficulty}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🔗 Immutable</h3>
            <p>Tamper-Proof</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Block verification details
    st.markdown("### 🔍 Block Verification")
    
    for i, block in enumerate(blockchain.chain):
        is_genesis = i == 0
        
        # Verify this block
        block_valid = True
        validation_issues = []
        
        if not is_genesis:
            if block.previous_hash != blockchain.chain[i-1].hash:
                block_valid = False
                validation_issues.append("Previous hash mismatch")
        
        if block.hash != block.calculate_hash():
            block_valid = False
            validation_issues.append("Hash calculation mismatch")
        
        status_icon = "✅" if block_valid else "❌"
        block_type = "Genesis Block" if is_genesis else f"Block {block.index}"
        
        with st.expander(f"{status_icon} {block_type} - Hash: {block.hash[:16]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Index:** {block.index}")
                st.markdown(f"**Timestamp:** {block.timestamp[:19]}")
                st.markdown(f"**Nonce:** {block.nonce}")
                st.markdown(f"**Hash:** `{block.hash}`")
            
            with col2:
                st.markdown(f"**Previous Hash:** `{block.previous_hash}`")
                if validation_issues:
                    st.error("Issues found:")
                    for issue in validation_issues:
                        st.error(f"- {issue}")
                else:
                    st.success("Block is valid")
            
            if not is_genesis and "patient_name" in block.data:
                st.markdown("**Patient Data (Encrypted View):**")
                st.json(block.data)

def database_management_page():
    """Database management page"""
    st.markdown("## 🗄 Database Management")
    
    # Get database statistics
    db_stats = get_database_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📊 Records in DB", db_stats['total_records_in_db'])
    
    with col2:
        st.metric("💾 Blockchain States", db_stats['blockchain_states'])
    
    with col3:
        if db_stats['oldest_record_date']:
            st.metric("📅 Oldest Record", db_stats['oldest_record_date'])
        else:
            st.metric("📅 Oldest Record", "No records")
    
    st.markdown("---")
    
    # Database operations
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Current State", help="Save current blockchain state to database"):
            save_blockchain_to_db(st.session_state.blockchain)
            st.success("Blockchain state saved to database!")
    
    with col2:
        if st.button("🔄 Load from Database", help="Load the most recent blockchain state"):
            loaded_blockchain = load_blockchain_from_db()
            if loaded_blockchain:
                st.session_state.blockchain = loaded_blockchain
                st.success("Blockchain loaded from database!")
                st.rerun()
            else:
                st.warning("No recent blockchain state found in database")
    
    st.markdown("---")
    
    # Cleanup operations
    st.markdown("### 🧹 Cleanup Operations")
    st.warning("⚠ Cleanup will remove data older than 7 days")
    
    if st.button("🗑 Cleanup Old Data", help="Remove data older than 7 days"):
        cleanup_old_data()
        st.success("Old data cleaned up successfully!")
    
    # Database info
    st.markdown("---")
    st.markdown("### ℹ Database Information")
    st.info("""
    **Database Features:**
    - 📊 Automatic persistence for at least 7 days
    - 💾 Blockchain state serialization
    - 🔍 Individual record storage for fast queries
    - 🧹 Automatic cleanup of old data
    - 🔄 Load/Save blockchain states
    
    **Files Created:**
    - ehr_blockchain.db - SQLite database file
    
    Your data is automatically saved when you add new records!
    """)

def dashboard_page():
    """Enhanced dashboard with statistics and visualizations"""
    st.markdown("## 📊 System Overview")
    
    # Get statistics
    stats = st.session_state.blockchain.get_statistics()
    db_stats = get_database_stats()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card pulse-animation">
            <h3>👥 {stats['total_patients']}</h3>
            <p>Total Patients</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📋 {stats['total_records']}</h3>
            <p>Medical Records</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⛓ {len(st.session_state.blockchain.chain)}</h3>
            <p>Blockchain Blocks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        is_valid = st.session_state.blockchain.validate_chain()
        status = "✅ Valid" if is_valid else "❌ Invalid"
        st.markdown(f"""
        <div class="metric-card">
            <h3>{status}</h3>
            <p>Chain Status</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Database status
    st.markdown("### 🗄 Database Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Records in Database", db_stats['total_records_in_db'])
    with col2:
        st.metric("Saved States", db_stats['blockchain_states'])
    
    # Visualizations
    if stats['total_records'] > 0:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Severity distribution pie chart
            if stats['severity_distribution']:
                fig_pie = px.pie(
                    values=list(stats['severity_distribution'].values()),
                    names=list(stats['severity_distribution'].keys()),
                    title="📈 Cases by Severity",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_pie.update_layout(height=400)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Records over time
            records = st.session_state.blockchain.get_all_records()
            if records:
                df = pd.DataFrame(records)
                df['date'] = pd.to_datetime(df['timestamp']).dt.date
                daily_records = df.groupby('date').size().reset_index(name='count')
                
                fig_line = px.line(
                    daily_records,
                    x='date',
                    y='count',
                    title="📅 Records Added Over Time",
                    markers=True
                )
                fig_line.update_layout(height=400)
                st.plotly_chart(fig_line, use_container_width=True)
    
    # Recent activity
    st.markdown("---")
    st.markdown("### 🕒 Recent Activity")
    recent_records = st.session_state.blockchain.get_all_records()[-5:]
    
    if recent_records:
        for record in reversed(recent_records):
            st.markdown(f"""
            <div class="record-card">
                <strong>Patient:</strong> {record['patient_name']} ({record['patient_id']}) | 
                <strong>Doctor:</strong> {record['doctor']} | 
                <strong>Time:</strong> {record['timestamp'][:19]}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent activity. Add some medical records to get started!")

def add_record_page():
    """Enhanced add record page with better UX"""
    st.markdown("## 📝 Add New Medical Record")
    
    with st.form("medical_record_form", clear_on_submit=True):
        st.markdown("### Patient Information")
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input("Patient ID*", placeholder="P001", help="Unique patient identifier")
            patient_name = st.text_input("Patient Name*", placeholder="John Doe")
            age = st.number_input("Age*", min_value=0, max_value=150, value=30)
        
        with col2:
            gender = st.selectbox("Gender*", ["Male", "Female", "Other"])
            hospital = st.text_input("Hospital*", placeholder="City General Hospital")
            doctor = st.text_input("Doctor Name*", placeholder="Dr. Smith")
        
        st.markdown("### Medical Information")
        col3, col4 = st.columns(2)
        
        with col3:
            diagnosis = st.text_area("Diagnosis*", placeholder="Patient diagnosis...", height=100)
            severity = st.selectbox("Severity Level*", ["Low", "Moderate", "High", "Critical"])
        
        with col4:
            treatment = st.text_area("Treatment Plan*", placeholder="Treatment details...", height=100)
        
        submitted = st.form_submit_button("🔐 Add to Blockchain", use_container_width=True)
        
        if submitted:
            if all([patient_id, patient_name, gender, diagnosis, treatment, doctor, hospital, severity]):
                record = MedicalRecord(
                    patient_id=patient_id,
                    patient_name=patient_name,
                    age=age,
                    gender=gender,
                    diagnosis=diagnosis,
                    treatment=treatment,
                    doctor=doctor,
                    hospital=hospital,
                    severity=severity,
                    timestamp=str(datetime.datetime.now())
                )
                
                st.markdown("### ⛏ Mining Block...")
                if st.session_state.blockchain.add_medical_record(record):
                    st.markdown("""
                    <div class="success-message">
                        ✅ Medical record successfully added to blockchain and saved to database!
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
            else:
                st.error("Please fill in all required fields (marked with *)")

def patient_records_page():
    """Enhanced patient records page with search and filtering"""
    st.markdown("## 🔍 Patient Records Management")
    
    # Search section
    col1, col2 = st.columns([2, 1])
    with col1:
        search_term = st.text_input("🔍 Search by Patient ID or Name:", placeholder="Enter patient ID or name")
    with col2:
        search_button = st.button("Search", use_container_width=True)
    
    records = st.session_state.blockchain.get_all_records()
    
    if records:
        # Filter records based on search
        if search_term:
            filtered_records = [
                record for record in records 
                if search_term.lower() in record['patient_id'].lower() or 
                   search_term.lower() in record['patient_name'].lower()
            ]
        else:
            filtered_records = records
        
        # Display filtering options
        col1, col2, col3 = st.columns(3)
        with col1:
            severity_filter = st.selectbox("Filter by Severity:", ["All"] + list(set([r['severity'] for r in records])))
        with col2:
            hospital_filter = st.selectbox("Filter by Hospital:", ["All"] + list(set([r['hospital'] for r in records])))
        with col3:
            doctor_filter = st.selectbox("Filter by Doctor:", ["All"] + list(set([r['doctor'] for r in records])))
        
        # Apply filters
        if severity_filter != "All":
            filtered_records = [r for r in filtered_records if r['severity'] == severity_filter]
        if hospital_filter != "All":
            filtered_records = [r for r in filtered_records if r['hospital'] == hospital_filter]
        if doctor_filter != "All":
            filtered_records = [r for r in filtered_records if r['doctor'] == doctor_filter]
        
        st.markdown(f"### 📋 Found {len(filtered_records)} record(s)")
        
        # Display records
        for record in filtered_records:
            severity_color = {
                "Low": "#28a745",
                "Moderate": "#ffc107", 
                "High": "#fd7e14",
                "Critical": "#dc3545"
            }.get(record['severity'], "#6c757d")
            
            st.markdown(f"""
            <div class="record-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4>👤 {record['patient_name']} ({record['patient_id']})</h4>
                    <span class="security-badge" style="background-color: {severity_color};">{record['severity']}</span>
                </div>
                <p><strong>Age:</strong> {record['age']} | <strong>Gender:</strong> {record['gender']}</p>
                <p><strong>🏥 Hospital:</strong> {record['hospital']} | <strong>👨‍⚕️ Doctor:</strong> {record['doctor']}</p>
                <p><strong>📊 Diagnosis:</strong> {record['diagnosis']}</p>
                <p><strong>💊 Treatment:</strong> {record['treatment']}</p>
                <p><strong>⏰ Recorded:</strong> {record['timestamp'][:19]}</p>
                <p><strong>🔗 Block:</strong> #{record['block_index']} | <strong>Hash:</strong> {record['block_hash'][:16]}...</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        st.info("No medical records found. Please add some records first.")

def blockchain_explorer_page():
    """Blockchain explorer with detailed block information"""
    st.markdown("## ⛓ Blockchain Explorer")
    
    blockchain = st.session_state.blockchain
    
    st.markdown(f"### Chain Overview - {len(blockchain.chain)} blocks")
    
    # Chain validation status
    is_valid = blockchain.validate_chain()
    if is_valid:
        st.success("✅ Blockchain integrity verified - All blocks are valid!")
    else:
        st.error("❌ Blockchain integrity compromised - Invalid blocks detected!")
    
    # Display each block
    for i, block in enumerate(blockchain.chain):
        is_genesis = i == 0
        
        # Block styling
        block_class = "genesis-block" if is_genesis else "blockchain-block"
        block_icon = "🏗" if is_genesis else "📦"
        block_title = "Genesis Block" if is_genesis else f"Block #{block.index}"
        
        with st.expander(f"{block_icon} {block_title} - {block.timestamp[:19]}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Block Information:**")
                st.code(f"""
Index: {block.index}
Timestamp: {block.timestamp}
Hash: {block.hash}
Previous Hash: {block.previous_hash}
Nonce: {block.nonce}
                """)
            
            with col2:
                st.markdown("**Block Data:**")
                if is_genesis:
                    st.json(block.data)
                else:
                    # Display medical record data in a more readable format
                    data = block.data
                    if isinstance(data, dict) and "patient_name" in data:
                        st.markdown(f"""
                        **Patient:** {data.get('patient_name', 'N/A')} ({data.get('patient_id', 'N/A')})  
                        **Age:** {data.get('age', 'N/A')} | **Gender:** {data.get('gender', 'N/A')}  
                        **Hospital:** {data.get('hospital', 'N/A')}  
                        **Doctor:** {data.get('doctor', 'N/A')}  
                        **Severity:** {data.get('severity', 'N/A')}  
                        **Diagnosis:** {data.get('diagnosis', 'N/A')}  
                        **Treatment:** {data.get('treatment', 'N/A')}
                        """)
                    else:
                        st.json(data)
            
            # Block verification
            st.markdown("---")
            if i > 0:  # Skip genesis block validation
                prev_hash_valid = block.previous_hash == blockchain.chain[i-1].hash
                hash_valid = block.hash == block.calculate_hash()
                
                col3, col4 = st.columns(2)
                with col3:
                    status = "✅ Valid" if prev_hash_valid else "❌ Invalid"
                    st.markdown(f"**Previous Hash Link:** {status}")
                
                with col4:
                    status = "✅ Valid" if hash_valid else "❌ Invalid"
                    st.markdown(f"**Hash Integrity:** {status}")

# Auto-cleanup on app start
cleanup_old_data()

# Run the main application
if __name__ == "__main__":
    main()
