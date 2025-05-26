import streamlit as st
import hashlib
import json
import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict
import pandas as pd

# Configure Streamlit page
st.set_page_config(
    page_title="Simple EHR Blockchain",
    page_icon="🏥",
    layout="wide"
)

@dataclass
class MedicalRecord:
    """Simple medical record structure"""
    patient_id: str
    patient_name: str
    age: int
    diagnosis: str
    treatment: str
    doctor: str
    timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

class Block:
    """Simple blockchain block"""
    def __init__(self, index: int, timestamp: str, data: Dict, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of the block"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def to_dict(self) -> Dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

class SimpleEHRBlockchain:
    """Simple EHR Blockchain implementation"""
    
    def __init__(self):
        self.chain: List[Block] = []
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            timestamp=str(datetime.datetime.now()),
            data={"message": "Genesis Block - EHR Blockchain Initialized"},
            previous_hash="0"
        )
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_medical_record(self, record: MedicalRecord) -> bool:
        """Add a new medical record to the blockchain"""
        try:
            new_block = Block(
                index=len(self.chain),
                timestamp=str(datetime.datetime.now()),
                data=record.to_dict(),
                previous_hash=self.get_latest_block().hash
            )
            self.chain.append(new_block)
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
    
    def validate_chain(self) -> bool:
        """Validate the integrity of the blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Check if current block's hash is valid
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if current block points to previous block
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True

# Initialize blockchain in session state
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = SimpleEHRBlockchain()

def main():
    st.title("🏥 Simple EHR Blockchain System")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Add Medical Record", "View All Records", "Patient Search", "Blockchain Info"]
    )
    
    if page == "Add Medical Record":
        add_medical_record_page()
    elif page == "View All Records":
        view_all_records_page()
    elif page == "Patient Search":
        patient_search_page()
    elif page == "Blockchain Info":
        blockchain_info_page()

def add_medical_record_page():
    st.header("📝 Add New Medical Record")
    
    with st.form("medical_record_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id = st.text_input("Patient ID*", placeholder="P001")
            patient_name = st.text_input("Patient Name*", placeholder="John Doe")
            age = st.number_input("Age*", min_value=0, max_value=150, value=30)
        
        with col2:
            diagnosis = st.text_area("Diagnosis*", placeholder="Patient diagnosis...")
            treatment = st.text_area("Treatment*", placeholder="Treatment plan...")
            doctor = st.text_input("Doctor Name*", placeholder="Dr. Smith")
        
        submitted = st.form_submit_button("Add Record to Blockchain")
        
        if submitted:
            if patient_id and patient_name and diagnosis and treatment and doctor:
                record = MedicalRecord(
                    patient_id=patient_id,
                    patient_name=patient_name,
                    age=age,
                    diagnosis=diagnosis,
                    treatment=treatment,
                    doctor=doctor,
                    timestamp=str(datetime.datetime.now())
                )
                
                if st.session_state.blockchain.add_medical_record(record):
                    st.success("✅ Medical record successfully added to blockchain!")
                    st.balloons()
                else:
                    st.error("❌ Failed to add record to blockchain")
            else:
                st.error("Please fill in all required fields (marked with *)")

def view_all_records_page():
    st.header("📋 All Medical Records")
    
    records = st.session_state.blockchain.get_all_records()
    
    if records:
        st.info(f"Total Records: {len(records)}")
        
        # Convert to DataFrame for better display
        df = pd.DataFrame(records)
        
        # Reorder columns for better readability
        column_order = ["patient_id", "patient_name", "age", "diagnosis", "treatment", "doctor", "timestamp", "block_index", "block_hash"]
        df = df[[col for col in column_order if col in df.columns]]
        
        st.dataframe(df, use_container_width=True)
        
        # Option to download as CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Records as CSV",
            data=csv,
            file_name=f"ehr_records_{datetime.date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.info("No medical records found in the blockchain.")

def patient_search_page():
    st.header("🔍 Search Patient Records")
    
    patient_id = st.text_input("Enter Patient ID to search:", placeholder="P001")
    
    if patient_id:
        records = st.session_state.blockchain.get_patient_records(patient_id)
        
        if records:
            st.success(f"Found {len(records)} record(s) for Patient ID: {patient_id}")
            
            for i, record in enumerate(records, 1):
                with st.expander(f"Record {i} - {record['timestamp'][:19]}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Patient Name:** {record['patient_name']}")
                        st.write(f"**Age:** {record['age']}")
                        st.write(f"**Doctor:** {record['doctor']}")
                    
                    with col2:
                        st.write(f"**Block Index:** {record['block_index']}")
                        st.write(f"**Block Hash:** `{record['block_hash'][:16]}...`")
                    
                    st.write(f"**Diagnosis:** {record['diagnosis']}")
                    st.write(f"**Treatment:** {record['treatment']}")
        else:
            st.warning(f"No records found for Patient ID: {patient_id}")

def blockchain_info_page():
    st.header("⛓️ Blockchain Information")
    
    blockchain = st.session_state.blockchain
    
    # Blockchain stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Blocks", len(blockchain.chain))
    
    with col2:
        st.metric("Medical Records", len(blockchain.get_all_records()))
    
    with col3:
        is_valid = blockchain.validate_chain()
        st.metric("Chain Valid", "✅ Yes" if is_valid else "❌ No")
    
    st.markdown("---")
    
    # Latest block info
    st.subheader("Latest Block Information")
    latest_block = blockchain.get_latest_block()
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Block Index:** {latest_block.index}")
        st.write(f"**Timestamp:** {latest_block.timestamp}")
        st.write(f"**Previous Hash:** `{latest_block.previous_hash[:32]}...`")
    
    with col2:
        st.write(f"**Current Hash:** `{latest_block.hash[:32]}...`")
        if latest_block.index > 0:
            st.write(f"**Data Type:** Medical Record")
        else:
            st.write(f"**Data Type:** Genesis Block")
    
    # Show full blockchain (for debugging)
    if st.checkbox("Show Full Blockchain (Debug Mode)"):
        st.subheader("Complete Blockchain")
        for block in blockchain.chain:
            with st.expander(f"Block {block.index} - Hash: {block.hash[:16]}..."):
                st.json(block.to_dict())

if __name__ == "__main__":
    main()
