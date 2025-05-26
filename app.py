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
    
    /* Blockchain visualization */
    .block-chain {
        display: flex;
        align-items: center;
        margin: 2rem 0;
    }
    
    .block {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0 10px;
        min-width: 150px;
        text-align: center;
        position: relative;
    }
    
    .block::after {
        content: '→';
        position: absolute;
        right: -25px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.5rem;
        color: #667eea;
    }
    
    .block:last-child::after {
        display: none;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
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
</style>
""", unsafe_allow_html=True)

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

# Initialize blockchain in session state
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = EnhancedEHRBlockchain()

def main():
    # Animated header
    st.markdown('<h1 class="animated-header">🏥 EHR Blockchain System</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation with icons
    st.sidebar.markdown("### 🚀 Navigation")
    pages = {
        "🏠 Dashboard": "Dashboard",
        "📝 Add Record": "Add Record", 
        "🔍 Patient Records": "Patient Records",
        "⛓️ Blockchain Explorer": "Blockchain Explorer"
    }
    
    selected_page = st.sidebar.selectbox("Choose a page:", list(pages.keys()))
    page = pages[selected_page]
    
    # Page routing
    if page == "Dashboard":
        dashboard_page()
    elif page == "Add Record":
        add_record_page()
    elif page == "Patient Records":
        patient_records_page()
    elif page == "Blockchain Explorer":
        blockchain_explorer_page()

def dashboard_page():
    """Enhanced dashboard with statistics and visualizations"""
    st.markdown("## 📊 System Overview")
    
    # Get statistics
    stats = st.session_state.blockchain.get_statistics()
    
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
            <h3>⛓️ {len(st.session_state.blockchain.chain)}</h3>
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
                
                st.markdown("### ⛏️ Mining Block...")
                if st.session_state.blockchain.add_medical_record(record):
                    st.markdown("""
                    <div class="success-message">
                        ✅ Medical record successfully added to blockchain!
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
        
        # Filters
        st.markdown("### 🎛️ Filters")
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
        
        st.markdown(f"### 📋 Records Found: {len(filtered_records)}")
        
        # Display records
        for i, record in enumerate(filtered_records):
            with st.expander(f"🏥 {record['patient_name']} ({record['patient_id']}) - {record['timestamp'][:19]}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**👤 Patient:** {record['patient_name']}")
                    st.markdown(f"**🆔 ID:** {record['patient_id']}")
                    st.markdown(f"**👶 Age:** {record['age']}")
                    st.markdown(f"**⚥ Gender:** {record['gender']}")
                    st.markdown(f"**🏥 Hospital:** {record['hospital']}")
                
                with col2:
                    st.markdown(f"**👨‍⚕️ Doctor:** {record['doctor']}")
                    st.markdown(f"**⚠️ Severity:** {record['severity']}")
                    st.markdown(f"**#️⃣ Block:** {record['block_index']}")
                    st.markdown(f"**🔗 Hash:** `{record['block_hash'][:16]}...`")
                
                st.markdown(f"**🔬 Diagnosis:** {record['diagnosis']}")
                st.markdown(f"**💊 Treatment:** {record['treatment']}")
        
        # Export functionality
        if filtered_records:
            st.markdown("---")
            df = pd.DataFrame(filtered_records)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Records as CSV",
                data=csv,
                file_name=f"ehr_records_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("📝 No medical records found in the blockchain. Add some records to get started!")

def blockchain_explorer_page():
    """Enhanced blockchain explorer with visualization"""
    st.markdown("## ⛓️ Blockchain Explorer")
    
    blockchain = st.session_state.blockchain
    
    # Blockchain visualization
    st.markdown("### 🔗 Blockchain Structure")
    
    # Create a simple blockchain visualization
    blocks_data = []
    for block in blockchain.chain:
        blocks_data.append({
            "Block": f"Block {block.index}",
            "Hash": block.hash[:8] + "...",
            "Previous": block.previous_hash[:8] + "..." if block.previous_hash != "0" else "Genesis",
            "Timestamp": block.timestamp[:19]
        })
    
    # Interactive blockchain chart
    if len(blocks_data) > 1:
        fig = go.Figure()
        
        x_pos = list(range(len(blocks_data)))
        y_pos = [0] * len(blocks_data)
        
        # Add blocks
        fig.add_trace(go.Scatter(
            x=x_pos,
            y=y_pos,
            mode='markers+text',
            marker=dict(size=30, color='lightblue', line=dict(width=2, color='darkblue')),
            text=[f"Block {i}" for i in range(len(blocks_data))],
            textposition="middle center",
            name="Blocks"
        ))
        
        # Add connections
        for i in range(len(x_pos)-1):
            fig.add_shape(
                type="line",
                x0=x_pos[i], y0=0, x1=x_pos[i+1], y1=0,
                line=dict(color="blue", width=3, dash="solid"),
            )
            fig.add_annotation(
                x=(x_pos[i] + x_pos[i+1])/2, y=0.1,
                text="→", showarrow=False,
                font=dict(size=20, color="blue")
            )
        
        fig.update_layout(
            title="Blockchain Structure Visualization",
            showlegend=False,
            height=200,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.3, 0.3])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Block details
    st.markdown("### 📋 Block Details")
    
    # Block selector
    block_options = [f"Block {i} ({'Genesis' if i == 0 else 'Medical Record'})" for i in range(len(blockchain.chain))]
    selected_block_idx = st.selectbox("Select a block to inspect:", range(len(block_options)), format_func=lambda x: block_options[x])
    
    if selected_block_idx is not None:
        block = blockchain.chain[selected_block_idx]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Block Information")
            st.json({
                "Index": block.index,
                "Timestamp": block.timestamp,
                "Hash": block.hash,
                "Previous Hash": block.previous_hash,
                "Nonce": block.nonce
            })
        
        with col2:
            st.markdown("#### Block Data")
            if block.index == 0:
                st.info("This is the Genesis Block")
            else:
                st.json(block.data)
    
    # Chain validation
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Validate Blockchain", use_container_width=True):
            with st.spinner("Validating blockchain integrity..."):
                time.sleep(1)  # Simulate validation time
                is_valid = blockchain.validate_chain()
                if is_valid:
                    st.success("✅ Blockchain is valid and secure!")
                else:
                    st.error("❌ Blockchain integrity compromised!")
    
    with col2:
        st.metric("Chain Length", len(blockchain.chain))
        st.metric("Difficulty", blockchain.difficulty)

if __name__ == "__main__":
    main()
