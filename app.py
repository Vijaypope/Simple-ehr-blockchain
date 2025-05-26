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
import random

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
    
    .block-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
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
    
    .data-initialization {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .severity-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .severity-low { background-color: #28a745; color: white; }
    .severity-moderate { background-color: #ffc107; color: black; }
    .severity-high { background-color: #fd7e14; color: white; }
    .severity-critical { background-color: #dc3545; color: white; }
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
    
    def add_medical_record(self, record: MedicalRecord, show_mining: bool = True) -> bool:
        """Add a new medical record to the blockchain with optional mining animation"""
        try:
            # Show mining process only if requested
            mining_placeholder = None
            if show_mining:
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
            
            if mining_placeholder:
                mining_placeholder.empty()
            return True
        except Exception as e:
            if show_mining:
                st.error(f"Error adding record: {str(e)}")
            return False
    
    def add_medical_record_silent(self, record: MedicalRecord) -> bool:
        """Add a medical record without UI feedback (for bulk operations)"""
        return self.add_medical_record(record, show_mining=False)
    
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

def get_sample_medical_data():
    """Generate realistic sample medical data for 15 patients"""
    sample_data = [
        {
            "patient_id": "P001",
            "patient_name": "Sam",
            "age": 45,
            "gender": "Male",
            "diagnosis": "Hypertension with mild cardiac complications",
            "treatment": "ACE inhibitors, lifestyle modifications, regular monitoring",
            "doctor": "Dr. Deepika",
            "hospital": "City General Hospital",
            "severity": "Moderate"
        },
        {
            "patient_id": "P002",
            "patient_name": "Sinthiya",
            "age": 32,
            "gender": "Female",
            "diagnosis": "Type 2 Diabetes Mellitus",
            "treatment": "Metformin, dietary counseling, glucose monitoring",
            "doctor": "Dr. Michael Chen",
            "hospital": "Metropolitan Medical Center",
            "severity": "Moderate"
        },
        {
            "patient_id": "P003",
            "patient_name": "Naveen",
            "age": 67,
            "gender": "Male",
            "diagnosis": "Coronary Artery Disease",
            "treatment": "Stent placement, dual antiplatelet therapy, cardiac rehabilitation",
            "doctor": "Dr. Amanda Rodriguez",
            "hospital": "Heart Care Institute",
            "severity": "High"
        },
        {
            "patient_id": "P004",
            "patient_name": "Ramya",
            "age": 28,
            "gender": "Female",
            "diagnosis": "Asthma with seasonal allergies",
            "treatment": "Inhaled corticosteroids, bronchodilators, allergy management",
            "doctor": "Dr. James Park",
            "hospital": "City General Hospital",
            "severity": "Low"
        },
        {
            "patient_id": "P005",
            "patient_name": "Mari Muthu",
            "age": 52,
            "gender": "Male",
            "diagnosis": "Chronic Kidney Disease Stage 3",
            "treatment": "ACE inhibitors, dietary restrictions, regular lab monitoring",
            "doctor": "Dr. Rachel Kim",
            "hospital": "Nephrology Specialists",
            "severity": "High"
        },
        {
            "patient_id": "P006",
            "patient_name": "Sangeetha",
            "age": 39,
            "gender": "Female",
            "diagnosis": "Rheumatoid Arthritis",
            "treatment": "Methotrexate, biologics, physical therapy",
            "doctor": "Dr. Thomas Anderson",
            "hospital": "Rheumatology Center",
            "severity": "Moderate"
        },
        {
            "patient_id": "P007",
            "patient_name": "Vikram",
            "age": 41,
            "gender": "Male",
            "diagnosis": "Major Depressive Disorder",
            "treatment": "SSRIs, cognitive behavioral therapy, lifestyle counseling",
            "doctor": "Dr. Susan Miller",
            "hospital": "Mental Health Associates",
            "severity": "Moderate"
        },
        {
            "patient_id": "P008",
            "patient_name": "Rohini",
            "age": 55,
            "gender": "Female",
            "diagnosis": "Osteoporosis with vertebral fractures",
            "treatment": "Bisphosphonates, calcium supplements, weight-bearing exercises",
            "doctor": "Dr. Kevin Wong",
            "hospital": "Bone Health Clinic",
            "severity": "High"
        },
        {
            "patient_id": "P009",
            "patient_name": "Subramani",
            "age": 36,
            "gender": "Male",
            "diagnosis": "Gastroesophageal Reflux Disease (GERD)",
            "treatment": "Proton pump inhibitors, dietary modifications, weight management",
            "doctor": "Dr. Maria Gonzalez",
            "hospital": "Digestive Health Center",
            "severity": "Low"
        },
        {
            "patient_id": "P010",
            "patient_name": "Anitha",
            "age": 29,
            "gender": "Female",
            "diagnosis": "Migraine with aura",
            "treatment": "Triptans, preventive medications, trigger avoidance",
            "doctor": "Dr. Daniel Lee",
            "hospital": "Neurology Institute",
            "severity": "Moderate"
        },
        {
            "patient_id": "P011",
            "patient_name": "Raja",
            "age": 61,
            "gender": "Male",
            "diagnosis": "Chronic Obstructive Pulmonary Disease (COPD)",
            "treatment": "Bronchodilators, inhaled steroids, pulmonary rehabilitation",
            "doctor": "Dr. Lisa Chen",
            "hospital": "Pulmonary Care Center",
            "severity": "High"
        },
        {
            "patient_id": "P012",
            "patient_name": "Jothika",
            "age": 43,
            "gender": "Female",
            "diagnosis": "Hypothyroidism",
            "treatment": "Levothyroxine therapy, regular TSH monitoring",
            "doctor": "Dr. Robert Kim",
            "hospital": "Endocrine Specialists",
            "severity": "Low"
        },
        {
            "patient_id": "P013",
            "patient_name": "Mani",
            "age": 38,
            "gender": "Male",
            "diagnosis": "Anxiety Disorder with panic attacks",
            "treatment": "Benzodiazepines, SSRIs, cognitive behavioral therapy",
            "doctor": "Dr. Nancy Davis",
            "hospital": "Mental Health Associates",
            "severity": "Moderate"
        },
        {
            "patient_id": "P014",
            "patient_name": "Renuka",
            "age": 50,
            "gender": "Female",
            "diagnosis": "Fibromyalgia syndrome",
            "treatment": "Pregabalin, physical therapy, stress management",
            "doctor": "Dr. Mark Wilson",
            "hospital": "Pain Management Clinic",
            "severity": "Moderate"
        },
        {
            "patient_id": "P015",
            "patient_name": "Kumar",
            "age": 72,
            "gender": "Male",
            "diagnosis": "Alzheimer's Disease - Early Stage",
            "treatment": "Cholinesterase inhibitors, cognitive stimulation, family support",
            "doctor": "Dr. Elizabeth Brown",
            "hospital": "Memory Care Center",
            "severity": "Critical"
        }
    ]
    return sample_data

def initialize_blockchain_with_data():
    """Initialize blockchain with sample patient data"""
    if 'blockchain_initialized' not in st.session_state:
        st.session_state.blockchain_initialized = False
    
    if not st.session_state.blockchain_initialized:
        sample_data = get_sample_medical_data()
        
        # Show initialization message
        init_placeholder = st.empty()
        init_placeholder.markdown("""
        <div class="data-initialization">
            🔄 Initializing blockchain with existing patient records...
        </div>
        """, unsafe_allow_html=True)
        
        # Add sample records to blockchain
        for i, data in enumerate(sample_data):
            # Create timestamps with some variation (simulate different admission times)
            base_time = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))
            timestamp = base_time + datetime.timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
            
            record = MedicalRecord(
                patient_id=data["patient_id"],
                patient_name=data["patient_name"],
                age=data["age"],
                gender=data["gender"],
                diagnosis=data["diagnosis"],
                treatment=data["treatment"],
                doctor=data["doctor"],
                hospital=data["hospital"],
                severity=data["severity"],
                timestamp=str(timestamp)
            )
            
            st.session_state.blockchain.add_medical_record_silent(record)
            
            # Update progress
            progress = (i + 1) / len(sample_data)
            init_placeholder.markdown(f"""
            <div class="data-initialization">
                🔄 Initializing blockchain... {i+1}/15 records added ({progress*100:.0f}%)
            </div>
            """, unsafe_allow_html=True)
        
        # Mark as initialized
        st.session_state.blockchain_initialized = True
        
        # Show completion message
        time.sleep(0.5)
        init_placeholder.markdown("""
        <div class="success-message">
            ✅ Blockchain initialized with 15 patient records!
        </div>
        """, unsafe_allow_html=True)
        time.sleep(2)
        init_placeholder.empty()

# Initialize blockchain in session state
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = EnhancedEHRBlockchain()

def main():
    # Initialize blockchain with sample data
    initialize_blockchain_with_data()
    
    # Animated header
    st.markdown('<h1 class="animated-header">🏥 EHR Blockchain System</h1>', unsafe_allow_html=True)
    
    # Show system status
    stats = st.session_state.blockchain.get_statistics()
    if stats['total_records'] > 0:
        st.markdown(f"""
        <div style="background: linear-gradient(90deg, #11998e 0%, #38ef7d 100%); 
                    color: white; padding: 0.5rem; border-radius: 5px; text-align: center; margin-bottom: 1rem;">
            💾 System Status: {stats['total_records']} patient records loaded in blockchain
        </div>
        """, unsafe_allow_html=True)
    
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
        
        # Hospital and Doctor distribution
        st.markdown("---")
        col3, col4 = st.columns(2)
        
        with col3:
            # Hospital distribution
            hospital_counts = pd.DataFrame(records)['hospital'].value_counts()
            fig_hospital = px.bar(
                x=hospital_counts.values,
                y=hospital_counts.index,
                orientation='h',
                title="🏥 Records by Hospital",
                color=hospital_counts.values,
                color_continuous_scale="Blues"
            )
            fig_hospital.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_hospital, use_container_width=True)
        
        with col4:
            # Age distribution
            ages = [record['age'] for record in records]
            fig_age = px.histogram(
                x=ages,
                nbins=10,
                title="👶 Age Distribution of Patients",
                color_discrete_sequence=['#667eea']
            )
            fig_age.update_layout(height=400)
            st.plotly_chart(fig_age, use_container_width=True)
    
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
            patient_id = st.text_input("Patient ID*", placeholder="P016", help="Unique patient identifier")
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
        
        st.markdown(f"### 📋 Found {len(filtered_records)} record(s)")
        
        # Display records
        if filtered_records:
            for i, record in enumerate(filtered_records):
                with st.expander(f"📄 {record['patient_name']} ({record['patient_id']}) - {record['diagnosis'][:50]}..."):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **Patient Information:**
                        - **ID:** {record['patient_id']}
                        - **Name:** {record['patient_name']}
                        - **Age:** {record['age']} years
                        - **Gender:** {record['gender']}
                        """)
                        
                        st.markdown(f"""
                        **Medical Details:**
                        - **Diagnosis:** {record['diagnosis']}
                        - **Severity:** <span class="severity-badge severity-{record['severity'].lower()}">{record['severity']}</span>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        **Care Information:**
                        - **Doctor:** {record['doctor']}
                        - **Hospital:** {record['hospital']}
                        - **Treatment:** {record['treatment']}
                        - **Date:** {record['timestamp'][:19]}
                        """)
                        
                        st.markdown(f"""
                        **Blockchain Info:**
                        - **Block:** #{record['block_index']}
                        - **Hash:** `{record['block_hash'][:16]}...`
                        """)
        else:
            st.info("No records found matching your search criteria.")
    else:
        st.info("No medical records found. Add some records to get started!")

def blockchain_explorer_page():
    """Enhanced blockchain explorer with detailed block information"""
    st.markdown("## ⛓️ Blockchain Explorer")
    
    # Blockchain statistics
    chain_length = len(st.session_state.blockchain.chain)
    is_valid = st.session_state.blockchain.validate_chain()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⛓️ {chain_length}</h3>
            <p>Total Blocks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_color = "#28a745" if is_valid else "#dc3545"
        status_text = "Valid" if is_valid else "Invalid"
        st.markdown(f"""
        <div class="metric-card" style="background: {status_color};">
            <h3>🔐 {status_text}</h3>
            <p>Chain Integrity</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        last_block = st.session_state.blockchain.get_latest_block()
        st.markdown(f"""
        <div class="metric-card">
            <h3>#{last_block.index}</h3>
            <p>Latest Block</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Blockchain visualization
    st.markdown("### 🔗 Blockchain Structure")
    
    # Show last 5 blocks in chain visualization
    recent_blocks = st.session_state.blockchain.chain[-5:]
    
    chain_html = '<div class="block-chain">'
    for block in recent_blocks:
        block_type = "Genesis" if block.index == 0 else f"Block #{block.index}"
        chain_html += f"""
        <div class="block">
            <strong>{block_type}</strong><br>
            Hash: {block.hash[:8]}...<br>
            Time: {block.timestamp[:10]}
        </div>
        """
    chain_html += '</div>'
    
    st.markdown(chain_html, unsafe_allow_html=True)
    
    # Detailed block explorer
    st.markdown("### 🔍 Block Details")
    
    selected_block_index = st.selectbox(
        "Select a block to examine:",
        range(len(st.session_state.blockchain.chain)),
        format_func=lambda x: f"Block #{x} {'(Genesis)' if x == 0 else ''}"
    )
    
    if selected_block_index is not None:
        block = st.session_state.blockchain.chain[selected_block_index]
        
        st.markdown(f"""
        <div class="block-card">
            <h3>🧱 Block #{block.index} Details</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Block Metadata:**")
            st.code(f"""
Index: {block.index}
Timestamp: {block.timestamp}
Hash: {block.hash}
Previous Hash: {block.previous_hash}
Nonce: {block.nonce}
            """)
        
        with col2:
            st.markdown("**Block Data:**")
            if block.index == 0:
                st.json(block.data)
            else:
                # Format medical record data nicely
                data = block.data
                st.markdown(f"""
                **Patient:** {data.get('patient_name', 'N/A')} ({data.get('patient_id', 'N/A')})  
                **Age:** {data.get('age', 'N/A')} | **Gender:** {data.get('gender', 'N/A')}  
                **Doctor:** {data.get('doctor', 'N/A')}  
                **Hospital:** {data.get('hospital', 'N/A')}  
                **Severity:** {data.get('severity', 'N/A')}  
                **Diagnosis:** {data.get('diagnosis', 'N/A')}  
                **Treatment:** {data.get('treatment', 'N/A')}
                """)
    
    # Chain validation section
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Validate Blockchain Integrity", use_container_width=True):
            with st.spinner("Validating blockchain..."):
                time.sleep(1)  # Simulate validation time
                is_valid = st.session_state.blockchain.validate_chain()
                
                if is_valid:
                    st.success("✅ Blockchain integrity verified! All blocks are valid.")
                else:
                    st.error("❌ Blockchain integrity compromised! Invalid blocks detected.")
    
    with col2:
        if st.button("📊 Export Blockchain Data", use_container_width=True):
            # Create downloadable JSON of the entire blockchain
            blockchain_data = []
            for block in st.session_state.blockchain.chain:
                blockchain_data.append(block.to_dict())
            
            st.download_button(
                label="💾 Download Blockchain JSON",
                data=json.dumps(blockchain_data, indent=2),
                file_name=f"ehr_blockchain_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# Main application
if __name__ == "__main__":
    main()
