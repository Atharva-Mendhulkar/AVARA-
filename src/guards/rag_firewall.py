from dataclasses import dataclass
from typing import List, Dict, Optional
import uuid

@dataclass
class DocumentProvenance:
    """Document Identity & Identity-based ACL tracking."""
    doc_id: str
    source_uri: str
    allowed_roles: List[str]  # e.g. ["analyst", "admin"]
    content_hash: str         # Ensure not maliciously altered

@dataclass
class RetrievedContext:
    """Context object returned by RAG after passing the firewall."""
    query: str
    text_content: str
    provenance: DocumentProvenance

class RAGFirewall:
    """
    Executes RAG Provenance Firewall rules:
    - Enforces document identity & ACLs
    - Assumes RAG output is untrusted input
    - Blocks instructions hidden in retrieved context
    """
    def __init__(self):
        self._document_registry: Dict[str, DocumentProvenance] = {}
        # Stub blocklist for instruction poisoning
        self._instruction_signatures = ["ignore previous instructions", "system proxy:", "execute immediately"]

    def register_document(self, prov: DocumentProvenance):
        """Register document ACLs for runtime retrieval validation."""
        self._document_registry[prov.doc_id] = prov
        
    def scan_for_instructions(self, text: str) -> bool:
        """
        Scan retrieved content for latent instructions (Poisoning).
        Returns True if safe, False if poisoned.
        """
        lower_text = text.lower()
        for signature in self._instruction_signatures:
            if signature in lower_text:
                print(f"RAG FIREWALL: Blocked content - Detected malicious instruction signature '{signature}'")
                return False
        return True

    def validate_retrieval(self, query: str, doc_id: str, content: str, agent_role: str) -> Optional[RetrievedContext]:
        """
        Intercepts vector search results. Validates ACLs and provenance.
        Returns RetrievedContext if safe, None (or raises) if blocked.
        """
        # 1. Document Identity tracking
        if doc_id not in self._document_registry:
            print(f"RAG FIREWALL Block: Document '{doc_id}' lacks provenance registration. Default deny.")
            return None
            
        prov = self._document_registry[doc_id]

        # 2. ACL Enforcement (Permission Bypass Prevention)
        # Vector similarity must not override access control
        user_is_admin = agent_role == "admin"
        if agent_role not in prov.allowed_roles and not user_is_admin:
            print(f"RAG FIREWALL Block: Agent role '{agent_role}' unauthorized to access document '{doc_id}'")
            return None
            
        # 3. Instruction Scan (Quarantine check)
        if not self.scan_for_instructions(content):
            print(f"RAG FIREWALL Quarantine: Content from '{doc_id}' is poisoned.")
            return None
            
        print(f"RAG FIREWALL Pass: Safe context injected from '{doc_id}'")
        return RetrievedContext(query=query, text_content=content, provenance=prov)
