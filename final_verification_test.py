#!/usr/bin/env python3
"""
Final verification test for the Contract Guardian feature.
This test verifies that all components work together correctly.
"""

import os
import tempfile
import fitz  # PyMuPDF
from agents.orchestrator import MasterOrchestratorAgent

def test_complete_workflow():
    """Test the complete contract analysis workflow"""
    print("=== Contract Guardian Feature - Final Verification Test ===\n")
    
    try:
        # 1. Test PDF creation and text extraction
        print("1. Testing PDF creation and text extraction...")
        
        # Create sample contract text
        sample_contract = """
        EMPLOYMENT AGREEMENT
        
        This Employment Agreement ("Agreement") is made and entered into as of January 1, 2024,
        by and between TechCorp Inc. ("Employer") and John Doe ("Employee").
        
        1. POSITION AND DUTIES
        Employee shall serve as Senior Software Engineer and perform such duties as are
        customarily associated with such position.
        
        2. COMPENSATION
        Base Salary: Employee shall receive an annual base salary of $85,000, payable in
        accordance with Employer's standard payroll practices.
        
        3. BENEFITS
        Paid Time Off: Employee shall be entitled to fifteen (15) days of paid time off per
        calendar year.
        
        4. TERM
        The initial term of this Agreement shall commence on January 1, 2024 and continue
        until December 31, 2024.
        
        5. SIGNING BONUS
        Employee shall receive a one-time signing bonus of $10,000 upon commencement of employment.
        
        6. TERMINATION
        This Agreement may be terminated by either party upon thirty (30) days written notice.
        
        7. NON-COMPETE
        During the term of employment and for a period of two (2) years thereafter, Employee
        shall not engage in any business that competes with Employer within a fifty (50) mile
        radius of Employer's principal place of business.
        
        8. CONFIDENTIALITY
        Employee agrees to maintain the confidentiality of all proprietary information of
        Employer both during and after employment.
        """
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file_path = temp_file.name
            
        # Create PDF with the sample contract
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), sample_contract)
        doc.save(temp_file_path)
        doc.close()
        
        print(f"   ✓ Created test PDF at: {temp_file_path}")
        
        # Extract text from the PDF
        doc = fitz.open(temp_file_path)
        contract_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            contract_text += page.get_text()
        doc.close()
        
        print(f"   ✓ Extracted {len(contract_text)} characters from PDF")
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        print("   ✓ Temporary file cleaned up")
        
        # 2. Test orchestrator initialization
        print("\n2. Testing orchestrator initialization...")
        orchestrator = MasterOrchestratorAgent()
        print("   ✓ Orchestrator initialized successfully")
        
        # 3. Test contract analysis
        print("\n3. Testing contract analysis...")
        result = orchestrator.route_request("contract", {"contract_text": contract_text})
        
        print(f"   ✓ Analysis completed - Success: {result.get('success')}")
        
        if result.get("success"):
            data = result.get("data", {})
            print(f"   ✓ Overall score: {data.get('overall_score', 'N/A')}")
            print(f"   ✓ Summary: {data.get('summary', 'N/A')[:50]}...")
            print(f"   ✓ Key terms extracted: {len(data.get('key_terms', {}))} terms")
            print(f"   ✓ Risk clauses identified: {len(data.get('risk_clauses', []))} clauses")
            
            # Verify required fields are present
            required_fields = ['overall_score', 'summary', 'key_terms', 'risk_clauses']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"   ⚠ Missing fields: {missing_fields}")
                return False
            else:
                print("   ✓ All required fields present in response")
                
            # Verify key terms structure
            key_terms = data.get('key_terms', {})
            required_key_terms = ['salary_base', 'start_date', 'pto_days', 'signing_bonus']
            missing_key_terms = [term for term in required_key_terms if term not in key_terms]
            
            if missing_key_terms:
                print(f"   ⚠ Missing key terms: {missing_key_terms}")
                return False
            else:
                print("   ✓ All required key terms present")
                
            # Verify risk clauses structure
            risk_clauses = data.get('risk_clauses', [])
            if risk_clauses:
                first_clause = risk_clauses[0]
                required_clause_fields = ['clause_name', 'risk_level', 'negotiation_strategy']
                missing_clause_fields = [field for field in required_clause_fields if field not in first_clause]
                
                if missing_clause_fields:
                    print(f"   ⚠ Missing clause fields: {missing_clause_fields}")
                    return False
                else:
                    print("   ✓ Risk clause structure verified")
            else:
                print("   ⚠ No risk clauses found")
                
            print("\n🎉 ALL TESTS PASSED - Contract Guardian feature is working correctly!")
            return True
            
        else:
            error = result.get("error", "Unknown error")
            print(f"   ❌ Analysis failed: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        print("\n✅ CONTRACT GUARDIAN FEATURE VERIFICATION: SUCCESS")
        exit(0)
    else:
        print("\n❌ CONTRACT GUARDIAN FEATURE VERIFICATION: FAILED")
        exit(1)