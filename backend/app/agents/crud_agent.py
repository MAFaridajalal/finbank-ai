"""
CRUD Agent for FinBank AI.
Handles Create, Update, and Delete operations for database records.
"""

from sqlalchemy import text
from app.agents.base import BaseAgent, AgentResult
import re
import json


def extract_json_from_llm_response(content: str) -> dict:
    """
    Extract JSON from LLM response.
    Handles cases where LLM returns extra text, code blocks, or explanations.
    """
    # Try to find JSON in code blocks first
    if "```json" in content:
        json_str = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        json_str = content.split("```")[1].split("```")[0].strip()
    else:
        json_str = content.strip()

    # If json_str still contains text before the JSON, try to extract just the JSON object
    # Look for the first { and last }
    if "{" in json_str and "}" in json_str:
        start_idx = json_str.find("{")
        end_idx = json_str.rfind("}") + 1
        json_str = json_str[start_idx:end_idx]

    return json.loads(json_str)


class CRUDAgent(BaseAgent):
    """Agent for creating, updating, and deleting database records."""

    name = "crud"
    description = "Creates, updates, or deletes customer, account, and transaction records"

    async def execute(self, task: str) -> AgentResult:
        """Execute a CRUD task."""
        try:
            # DEBUG: Print received task
            print(f"\n{'='*60}")
            print(f"CRUD AGENT EXECUTE: Received task: {task}")

            # Detect operation type
            operation = self.detect_operation(task)
            print(f"CRUD AGENT: Detected operation: {operation}")
            print(f"{'='*60}\n")

            if operation == "CREATE":
                return await self.handle_create(task)
            elif operation == "UPDATE":
                return await self.handle_update(task)
            elif operation == "DELETE":
                return await self.handle_delete(task)
            else:
                return AgentResult(
                    success=False,
                    data=None,
                    message="I can help you CREATE, UPDATE, or DELETE records. Please specify what you'd like to do.",
                )

        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                message=f"CRUD operation failed: {str(e)}",
            )

    def detect_operation(self, task: str) -> str:
        """Detect the type of CRUD operation from the task description."""
        task_lower = task.lower()

        # Check UPDATE first (more specific than CREATE)
        if any(word in task_lower for word in ['update', 'modify', 'change', 'edit']):
            return "UPDATE"

        # DELETE keywords
        if any(word in task_lower for word in ['delete', 'remove', 'deactivate']):
            return "DELETE"

        # CREATE keywords (check last to avoid conflicts)
        if any(word in task_lower for word in ['add', 'create', 'insert', 'new', 'register']):
            return "CREATE"

        return "UNKNOWN"

    async def handle_create(self, task: str) -> AgentResult:
        """Handle CREATE operations."""
        # Check if it's a customer creation
        if 'customer' in task.lower() or 'user' in task.lower():
            return await self.create_customer(task)
        else:
            return AgentResult(
                success=False,
                data=None,
                message="Currently I can only create customers. Please specify what you'd like to create.",
            )

    async def create_customer(self, task: str) -> AgentResult:
        """Create a new customer."""
        # Extract information from the task using LLM
        extraction_prompt = f"""Extract customer information from this request: "{task}"

Return ONLY a JSON object with these fields (use null for missing fields):
{{
    "first_name": "...",
    "last_name": "...",
    "email": "...",
    "phone": "...",
    "address": "...",
    "city": "...",
    "tier": "Basic|Premium|VIP",
    "branch": "Downtown|Westside|Airport|Bellevue"
}}

If any REQUIRED field (first_name, last_name, email) is missing, return:
{{
    "missing": ["field1", "field2", ...]
}}
"""

        response = await self.llm.generate(
            prompt=extraction_prompt,
            system_prompt="You are a data extraction assistant. Return ONLY valid JSON, nothing else.",
            temperature=0.1,
            max_tokens=300
        )

        # DEBUG: Print LLM response
        print(f"CRUD AGENT: LLM extraction response: {response.content}")

        # Parse the response
        try:
            data = extract_json_from_llm_response(response.content)
            print(f"CRUD AGENT: Parsed data: {data}")

            # Check if there are missing fields
            if "missing" in data:
                missing_fields = ", ".join(data["missing"])
                return AgentResult(
                    success=False,
                    data={"missing_fields": data["missing"]},
                    message=f"I need more information to create a customer. Please provide: {missing_fields}",
                )

            # Validate required fields
            required = ["first_name", "last_name", "email"]
            missing = [f for f in required if not data.get(f)]
            if missing:
                return AgentResult(
                    success=False,
                    data={"missing_fields": missing},
                    message=f"Required fields missing: {', '.join(missing)}. Please provide these details.",
                )

            # Get tier_id and branch_id
            tier_map = {"basic": 1, "premium": 2, "vip": 3}
            branch_map = {"downtown": 1, "westside": 2, "airport": 3, "bellevue": 4}

            tier_id = tier_map.get(data.get("tier", "basic").lower(), 1)
            branch_id = branch_map.get(data.get("branch", "downtown").lower(), 1)

            # Check if email already exists
            existing = self.db.execute(text(
                "SELECT id FROM customers WHERE email = :email"
            ), {"email": data["email"]}).first()

            if existing:
                return AgentResult(
                    success=False,
                    data=None,
                    message=f"A customer with email {data['email']} already exists (ID: {existing[0]})",
                )

            # Insert the customer
            insert_data = {
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "email": data["email"],
                "phone": data.get("phone", ""),
                "address": data.get("address", ""),
                "city": data.get("city", ""),
                "tier_id": tier_id,
                "branch_id": branch_id
            }
            print(f"CRUD AGENT: Inserting customer with data: {insert_data}")

            result = self.db.execute(text("""
                INSERT INTO customers
                (first_name, last_name, email, phone, address, city, tier_id, branch_id)
                VALUES
                (:first_name, :last_name, :email, :phone, :address, :city, :tier_id, :branch_id)
            """), insert_data)

            self.db.commit()
            print(f"CRUD AGENT: Customer inserted successfully, ID: {result.lastrowid}")

            # Get the new customer ID
            new_id = result.lastrowid

            return AgentResult(
                success=True,
                data={"customer_id": new_id, **data},
                message=f"✅ Successfully created customer: {data['first_name']} {data['last_name']} (ID: {new_id})",
            )

        except json.JSONDecodeError:
            return AgentResult(
                success=False,
                data=None,
                message=f"Failed to parse customer information. Please provide details in a clearer format.",
            )

    async def handle_update(self, task: str) -> AgentResult:
        """Handle UPDATE operations."""
        # Try regex extraction first (more reliable than LLM)
        print(f"CRUD AGENT UPDATE: Parsing task: {task}")

        # Pattern 1: "customer <ID>" anywhere in text
        pattern_id = r"customer\s+(\d+)"
        match_id = re.search(pattern_id, task, re.IGNORECASE)

        # Pattern 2: Look for customer names - multiple strategies
        # Strategy 1: "Update/Change [customer] FirstName LastName"
        # Strategy 2: Named "named X Y" pattern
        # Strategy 3: Generic two capitalized words (excluding field names)
        pattern_name_list = [
            r"(?:update|change|modify)\s+(?:customer\s+)?([A-Z][a-zA-Z]+)\s+([A-Z][a-zA-Z]+)(?:,|\s|'s|$)",
            r"named\s+([A-Z][a-zA-Z]+)\s+([A-Z][a-zA-Z]+)",
            r"customer\s+([A-Z][a-zA-Z]+)\s+([A-Z][a-zA-Z]+)",
        ]

        excluded_words = ['first', 'last', 'email', 'phone', 'update', 'change', 'modify', 'delete', 'remove']
        excluded_second = ['name', 'address', 'email', 'phone', 'user']

        match_name = None
        for pattern in pattern_name_list:
            match_name = re.search(pattern, task, re.IGNORECASE)
            if match_name:
                first_word = match_name.group(1).lower()
                second_word = match_name.group(2).lower()
                if first_word not in excluded_words and second_word not in excluded_second:
                    break
                match_name = None

        # Extract field updates
        fields = {}

        # Email pattern - look for actual email addresses
        email_match = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", task)
        if email_match:
            fields["email"] = email_match.group(1)

        # Last name pattern - "last name to NewName" or "lastname of X to NewName"
        # Look for the word immediately after "to" when "last name" is mentioned
        if 'last' in task.lower() and 'name' in task.lower():
            lastname_match = re.search(r"last\s*name\s+(?:of\s+[^t]+?\s+)?to\s+([A-Z][a-zA-Z]+)", task, re.IGNORECASE)
            if lastname_match:
                fields["last_name"] = lastname_match.group(1)

        # First name pattern
        if 'first' in task.lower() and 'name' in task.lower():
            firstname_match = re.search(r"first\s*name\s+(?:of\s+[^t]+?\s+)?to\s+([A-Z][a-zA-Z]+)", task, re.IGNORECASE)
            if firstname_match:
                fields["first_name"] = firstname_match.group(1)

        # Phone pattern
        phone_match = re.search(r"phone\s+(?:number\s+)?(?:to\s+)?([\d-]+)", task, re.IGNORECASE)
        if phone_match:
            fields["phone"] = phone_match.group(1)

        # Build data dictionary
        data = {}
        if match_id:
            data["customer_id"] = int(match_id.group(1))
            data["fields"] = fields
        elif match_name:
            data["first_name"] = match_name.group(1)
            data["last_name"] = match_name.group(2)
            data["fields"] = fields
        else:
            data["missing"] = "identifier"

        print(f"CRUD AGENT UPDATE: Extracted data via regex: {data}")

        try:

            if "missing" in data:
                return AgentResult(
                    success=False,
                    data=None,
                    message="Please specify which customer to update (by ID or name).",
                )

            customer_id = data.get("customer_id")

            # If no ID provided, try to find by name
            if not customer_id:
                first_name = data.get("first_name")
                last_name = data.get("last_name")

                if not first_name and not last_name:
                    return AgentResult(
                        success=False,
                        data=None,
                        message="Please specify the customer ID or name to update.",
                    )

                # Search by name
                print(f"CRUD AGENT UPDATE: Searching for customer by name: {first_name} {last_name}")
                query_parts = []
                params = {}

                if first_name:
                    query_parts.append("LOWER(first_name) = LOWER(:first_name)")
                    params["first_name"] = first_name
                if last_name:
                    query_parts.append("LOWER(last_name) = LOWER(:last_name)")
                    params["last_name"] = last_name

                search_sql = f"SELECT id, first_name, last_name FROM customers WHERE {' AND '.join(query_parts)}"
                existing = self.db.execute(text(search_sql), params).first()

                if not existing:
                    return AgentResult(
                        success=False,
                        data=None,
                        message=f"Customer '{first_name} {last_name}' not found.",
                    )

                customer_id = existing[0]
                print(f"CRUD AGENT UPDATE: Found customer ID: {customer_id}")
            else:
                # Check if customer exists by ID
                existing = self.db.execute(text(
                    "SELECT id, first_name, last_name FROM customers WHERE id = :id"
                ), {"id": customer_id}).first()

                if not existing:
                    return AgentResult(
                        success=False,
                        data=None,
                        message=f"Customer with ID {customer_id} not found.",
                    )

            fields = data.get("fields", {})
            if not fields:
                return AgentResult(
                    success=False,
                    data=None,
                    message="Please specify which fields to update.",
                )

            # Build UPDATE query
            set_clauses = []
            params = {"id": customer_id}

            # Map tier/branch names to IDs
            tier_map = {"basic": 1, "premium": 2, "vip": 3}
            branch_map = {"downtown": 1, "westside": 2, "airport": 3, "bellevue": 4}

            for field, value in fields.items():
                if value is None:
                    continue

                if field == "tier":
                    set_clauses.append("tier_id = :tier_id")
                    params["tier_id"] = tier_map.get(value.lower(), 1)
                elif field == "branch":
                    set_clauses.append("branch_id = :branch_id")
                    params["branch_id"] = branch_map.get(value.lower(), 1)
                elif field in ["first_name", "last_name", "email", "phone", "address", "city"]:
                    set_clauses.append(f"{field} = :{field}")
                    params[field] = value

            if not set_clauses:
                return AgentResult(
                    success=False,
                    data=None,
                    message="No valid fields to update.",
                )

            # Execute UPDATE
            sql = f"UPDATE customers SET {', '.join(set_clauses)} WHERE id = :id"
            self.db.execute(text(sql), params)
            self.db.commit()

            return AgentResult(
                success=True,
                data={"customer_id": customer_id, "updated_fields": list(fields.keys())},
                message=f"✅ Successfully updated customer {existing[1]} {existing[2]} (ID: {customer_id})",
            )

        except json.JSONDecodeError:
            return AgentResult(
                success=False,
                data=None,
                message="Failed to parse update information.",
            )

    async def handle_delete(self, task: str) -> AgentResult:
        """Handle DELETE operations."""
        # Try regex extraction first (more reliable than LLM)
        print(f"CRUD AGENT DELETE: Parsing task: {task}")

        # Pattern 1: "Delete customer <ID>"
        pattern_id = r"customer\s+(\d+)"
        match_id = re.search(pattern_id, task, re.IGNORECASE)

        # Pattern 2: Look for customer names - multiple strategies
        pattern_name_list = [
            r"(?:delete|remove)\s+(?:customer\s+)?([A-Z][a-zA-Z]+)\s+([A-Z][a-zA-Z]+)",
            r"named\s+([A-Z][a-zA-Z]+)\s+([A-Z][a-zA-Z]+)",
            r"customer\s+([A-Z][a-zA-Z]+)\s+([A-Z][a-zA-Z]+)",
        ]

        excluded_words = ['delete', 'remove', 'customer']

        match_name = None
        for pattern in pattern_name_list:
            match_name = re.search(pattern, task, re.IGNORECASE)
            if match_name:
                first_word = match_name.group(1).lower()
                if first_word not in excluded_words:
                    break
                match_name = None

        # Build data dictionary
        data = {}
        if match_id:
            data["customer_id"] = int(match_id.group(1))
        elif match_name:
            data["first_name"] = match_name.group(1)
            data["last_name"] = match_name.group(2)
        else:
            data["missing"] = "identifier"

        print(f"CRUD AGENT DELETE: Extracted data via regex: {data}")

        try:

            if "missing" in data:
                return AgentResult(
                    success=False,
                    data=None,
                    message="Please specify which customer to delete (by ID or name).",
                )

            customer_id = data.get("customer_id")

            # If no ID provided, try to find by name
            if not customer_id:
                first_name = data.get("first_name")
                last_name = data.get("last_name")

                if not first_name and not last_name:
                    return AgentResult(
                        success=False,
                        data=None,
                        message="Please specify the customer ID or name to delete.",
                    )

                # Search by name
                print(f"CRUD AGENT DELETE: Searching for customer by name: {first_name} {last_name}")
                query_parts = []
                params = {}

                if first_name:
                    query_parts.append("LOWER(first_name) = LOWER(:first_name)")
                    params["first_name"] = first_name
                if last_name:
                    query_parts.append("LOWER(last_name) = LOWER(:last_name)")
                    params["last_name"] = last_name

                search_sql = f"SELECT id, first_name, last_name, email FROM customers WHERE {' AND '.join(query_parts)}"
                existing = self.db.execute(text(search_sql), params).first()

                if not existing:
                    return AgentResult(
                        success=False,
                        data=None,
                        message=f"Customer '{first_name} {last_name}' not found.",
                    )

                customer_id = existing[0]
                print(f"CRUD AGENT DELETE: Found customer ID: {customer_id}")
            else:
                # Check if customer exists by ID
                existing = self.db.execute(text(
                    "SELECT id, first_name, last_name, email FROM customers WHERE id = :id"
                ), {"id": customer_id}).first()

            if not existing:
                return AgentResult(
                    success=False,
                    data=None,
                    message=f"Customer with ID {customer_id} not found.",
                )

            # Check for related records (accounts)
            account_count = self.db.execute(text(
                "SELECT COUNT(*) FROM accounts WHERE customer_id = :id"
            ), {"id": customer_id}).scalar()

            if account_count > 0:
                return AgentResult(
                    success=False,
                    data=None,
                    message=f"Cannot delete customer {existing[1]} {existing[2]} - they have {account_count} active account(s). Please close accounts first.",
                )

            # Delete the customer
            self.db.execute(text("DELETE FROM customers WHERE id = :id"), {"id": customer_id})
            self.db.commit()

            return AgentResult(
                success=True,
                data={"customer_id": customer_id, "name": f"{existing[1]} {existing[2]}"},
                message=f"✅ Successfully deleted customer: {existing[1]} {existing[2]} (ID: {customer_id})",
            )

        except json.JSONDecodeError:
            return AgentResult(
                success=False,
                data=None,
                message="Failed to parse delete request.",
            )
