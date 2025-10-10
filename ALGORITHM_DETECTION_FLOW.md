# Algorithm Detection Flow - Optimized

## Overview
This document describes the optimized algorithm detection flow for both **Certificate Upload** and **Domain Scanner** features.

---

## 🔄 **NEW OPTIMIZED FLOW**

### **Phase 1: Certificate Parsing**
1. Extract certificate details (subject, issuer, validity dates)
2. Parse public key and signature algorithm
3. Catch `ValueError` for PQC algorithms (cryptography library doesn't support them yet)
4. Extract OID from error message: `"Unknown key type: 2.16.840.1.101.3.4.3.18"`

---

### **Phase 2: Algorithm Detection (Priority Order)**

#### **Step 1: OID-Based Database Lookup (PRIORITY 1)** ⭐
```python
# Try OID lookup FIRST
if public_key_oid:
    public_key_info = db.query(PublicKeyAlgorithm).filter(
        PublicKeyAlgorithm.public_key_algorithm_oid == public_key_oid
    ).first()
    
    if public_key_info:
        ✅ FOUND - Use database information
        - Algorithm name: public_key_info.name
        - Description: public_key_info.description
        - Security level: public_key_info.security_level
        - Is PQC: public_key_info.is_pqc
        - Is quantum safe: public_key_info.is_quantum_safe
```

#### **Step 2: Name-Based Database Lookup (FALLBACK)** 🔄
```python
# If OID lookup failed, try name-based lookup
if not public_key_info and public_key_algo:
    public_key_info = db.query(PublicKeyAlgorithm).filter(
        PublicKeyAlgorithm.name.ilike(f"%{public_key_algo}%")
    ).first()
    
    if public_key_info:
        ✅ FOUND - Use database information
```

#### **Step 3: Hardcoded PQC OID Mapping (LAST RESORT)** 🆘
```python
# If database doesn't have the OID, use hardcoded mapping
pqc_oid_map = {
    "2.16.840.1.101.3.4.3.17": "ML-DSA-65",
    "2.16.840.1.101.3.4.3.18": "ML-DSA-87",
    "2.16.840.1.101.3.4.4.1": "ML-KEM-512",
    "2.16.840.1.101.3.4.4.2": "ML-KEM-768",
    "2.16.840.1.101.3.4.4.3": "ML-KEM-1024",
    "1.3.6.1.4.1.2.267.7.4.4": "CRYSTALS-Dilithium",
    "1.3.6.1.4.1.2.267.7.6.5": "CRYSTALS-Kyber",
}

if public_key_oid in pqc_oid_map:
    algorithm_name = pqc_oid_map[public_key_oid]
```

---

### **Phase 3: Quantum Safety Determination**
```python
quantum_safe = False

# Check from database info
if public_key_info and public_key_info.is_quantum_safe:
    quantum_safe = True
    
if signature_info and signature_info.is_quantum_safe:
    quantum_safe = True

# Check if detected as PQC
if is_pqc:
    quantum_safe = True
```

---

### **Phase 4: AI Recommendation with Enriched Context** 🤖

#### **Context Building**
```python
context = {
    "algorithm_type": "certificate_analysis",
    "key_size": public_key_size,
    "certificate_type": "X.509",
    "expiry_date": valid_until.isoformat(),
    "issuer": issuer,
    "is_pqc": is_pqc,
    "quantum_safe": quantum_safe,
    "current_usage": "TLS/SSL Certificate"
}

# ADD DATABASE DETAILS for better AI analysis
if public_key_info:
    context["public_key_details"] = {
        "name": public_key_info.name,
        "description": public_key_info.description,
        "security_level": public_key_info.security_level,
        "is_quantum_safe": public_key_info.is_quantum_safe,
        "is_pqc": public_key_info.is_pqc,
        "key_size": public_key_info.key_size,
        "oid": public_key_info.public_key_algorithm_oid
    }

if signature_info:
    context["signature_details"] = {
        "name": signature_info.name,
        "description": signature_info.description,
        "security_level": signature_info.security_level,
        "is_quantum_safe": signature_info.is_quantum_safe,
        "is_pqc": signature_info.is_pqc,
        "oid": signature_info.signature_algorithm_oid
    }
```

#### **AI Analysis**
```python
# Call Gemini AI with enriched context
ai_recommendation = await _get_gemini_recommendations(
    public_key_algo,
    "public_key",
    context  # Contains database details!
)
```

---

## 📊 **Data Flow Diagram**

```
Certificate (PEM/DER)
        ↓
Parse Certificate
        ↓
Extract OID: "2.16.840.1.101.3.4.3.18"
        ↓
┌───────────────────────────────────┐
│ STEP 1: OID-Based DB Lookup      │ ⭐ PRIORITY 1
│ Query: WHERE oid = "2.16.840..." │
└───────────────────────────────────┘
        ↓
   Found in DB? ────YES────→ Use DB data ✅
        │                         ↓
        NO                   Get Details:
        ↓                    - Name: ML-DSA-87
                             - Description
┌───────────────────────────────────┐ - Security Level
│ STEP 2: Name-Based DB Lookup      │ - Is PQC: true
│ Query: WHERE name LIKE "%ML-DSA%" │ - Is Quantum Safe: true
└───────────────────────────────────┘
        ↓
   Found in DB? ────YES────→ Use DB data ✅
        │
        NO
        ↓
┌───────────────────────────────────┐
│ STEP 3: Hardcoded OID Mapping     │ 🆘 LAST RESORT
│ pqc_oid_map["2.16.840..."]        │
└───────────────────────────────────┘
        ↓
   Found in Map? ────YES────→ Use hardcoded name
        │                     "ML-DSA-87"
        NO
        ↓
   Mark as "Unknown PQC"
        ↓
┌───────────────────────────────────┐
│ Build AI Context with DB Details  │
│ - Algorithm info from DB           │
│ - Security levels                  │
│ - Quantum safety flags             │
│ - Descriptions                     │
└───────────────────────────────────┘
        ↓
┌───────────────────────────────────┐
│ Call Gemini AI                     │
│ _get_gemini_recommendations()      │
│ with enriched context              │
└───────────────────────────────────┘
        ↓
   Return Analysis with:
   - Quantum vulnerability assessment
   - Recommended PQC algorithms
   - Migration strategy
   - Implementation guide
   - Compliance notes
```

---

## 🎯 **Key Improvements**

### **1. Database-First Approach**
- ✅ **OID lookup is PRIORITY 1** (most accurate)
- ✅ **Name-based lookup is fallback** (when OID not in DB)
- ✅ **Hardcoded map is last resort** (ensures system always works)

### **2. Enriched AI Context**
- ✅ AI receives **database details** (descriptions, security levels)
- ✅ AI knows **exact quantum safety status** from DB
- ✅ AI has **OID information** for precise recommendations
- ✅ Better recommendations based on **authoritative data**

### **3. Consistent Behavior**
- ✅ **Same flow** for Upload Certificate and Domain Scanner
- ✅ **Same database queries**
- ✅ **Same AI analysis**
- ✅ **Consistent user experience**

---

## 🔍 **Example: ML-DSA-87 Detection**

### **Input:** Certificate with OID `2.16.840.1.101.3.4.3.18`

### **Processing:**
1. **Parse certificate** → Catch `ValueError`
2. **Extract OID** → `2.16.840.1.101.3.4.3.18`
3. **Database OID lookup**:
   ```sql
   SELECT * FROM PublicKeyAlgorithm 
   WHERE public_key_algorithm_oid = '2.16.840.1.101.3.4.3.18'
   ```
   Result: ✅ Found!
   ```json
   {
     "name": "ML-DSA-87",
     "description": "NIST ML-DSA (Module-Lattice-Based Digital Signature Algorithm)",
     "security_level": "High",
     "is_pqc": true,
     "is_quantum_safe": true,
     "key_size": 1952,
     "public_key_algorithm_oid": "2.16.840.1.101.3.4.3.18"
   }
   ```

4. **Build AI context** with database details
5. **Call Gemini AI** with enriched context:
   ```python
   context = {
       "algorithm_type": "certificate_analysis",
       "is_pqc": true,
       "quantum_safe": true,
       "public_key_details": {
           "name": "ML-DSA-87",
           "description": "NIST ML-DSA...",
           "security_level": "High",
           "is_quantum_safe": true,
           "oid": "2.16.840.1.101.3.4.3.18"
       }
   }
   ```

6. **AI Response**:
   ```json
   {
     "quantum_vulnerability": "SECURE - Already using quantum-safe algorithms",
     "primary_recommendation": "✅ Certificate uses ML-DSA-87, a NIST-standardized PQC algorithm",
     "security_assessment": "🔐 This certificate is protected against quantum attacks",
     "compliance_notes": "✅ Compliant with NIST Post-Quantum Cryptography standards"
   }
   ```

---

## 📝 **Logging for Debugging**

The system logs every step:

```
INFO: Detected public key OID: 2.16.840.1.101.3.4.3.18
INFO: Attempting OID-based lookup for public key: 2.16.840.1.101.3.4.3.18
INFO: ✅ Found public key algorithm in DB by OID: ML-DSA-87
INFO: Added public key DB details to AI context: ML-DSA-87
INFO: Attempting OID-based lookup for signature: 1.2.840.113549.1.1.11
INFO: ✅ Found signature algorithm in DB by OID: SHA256-RSA
INFO: Added signature DB details to AI context: SHA256-RSA
```

---

## 🚀 **Benefits**

1. **More Accurate Detection**: Database is source of truth
2. **Better AI Recommendations**: Enriched context from database
3. **Graceful Degradation**: Falls back to hardcoded map if DB unavailable
4. **Detailed Logging**: Easy to debug and monitor
5. **Future-Proof**: New algorithms can be added to database without code changes

---

## 📚 **Database Schema**

### **PublicKeyAlgorithm Table**
```sql
CREATE TABLE PublicKeyAlgorithm (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    public_key_algorithm_oid VARCHAR(255),
    public_key_algorithm_name VARCHAR(255),
    key_size INT,
    security_level VARCHAR(50),
    is_quantum_safe BIT,
    is_pqc BIT
)
```

### **SignatureAlgorithm Table**
```sql
CREATE TABLE SignatureAlgorithm (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    signature_algorithm_oid VARCHAR(255),
    signature_algorithm_name VARCHAR(255),
    security_level VARCHAR(50),
    is_quantum_safe BIT,
    is_pqc BIT
)
```

---

## ✅ **Status**

- ✅ Implemented in `analyze_certificate_data()` (lines 1210-1500)
- ✅ OID-based lookup FIRST
- ✅ Name-based lookup as fallback
- ✅ Database details passed to Gemini AI
- ✅ Quantum safety determined from DB data
- ✅ Comprehensive logging
- ✅ Used by both Upload Certificate and Domain Scanner
