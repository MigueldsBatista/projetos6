This bulk ingestion strategy with the **Adapter** pattern ensures scalability and maintainability, supporting **DataJud** now and other sources (official gazettes, court APIs) in the future.

Here is the **Reverse Engineering** structure for this logical flow:

### 3. Reverse Engineering and Programming Logic (The "How")

#### **A. Data Input and Sources**

* **Data Entry:** Data enters the system through **HTTP GET/POST** requests to the DataJud `_search` endpoint. The system uses a dynamic `size` parameter (e.g., 50) to extract the maximum number of matches per request, optimizing case collection from **TRT6**.

* **External Sources:** The feature depends on the **CNJ Public API (DataJud)**. The system implements the **Adapter** pattern to translate the API's native JSON (such as `subjects` and `movements` fields) into a unified interface for the internal dataset.

#### **B. Processing and Business Logic (Backend)**

* **Triggers:** The flow is triggered by a synchronization job that sends the topic list and receives the data batch from the API.

* **Algorithms:**
    * **Deduplication:** A method receives the Adapter's object list and performs a set difference operation, comparing the `caseNumber` with existing database records to filter only new items.
    * **Vectorization:** After filtering, new records pass through **NLP** models to generate **embeddings** from summaries before persistence.

* **Data Structure:** The system uses a **hybrid** architecture:
    * **Relational:** Where **Bulk Create** executes to save metadata (amounts, dates, courts) atomically and performantly.
    * **Vector:** Where corresponding vectors are stored to enable similarity search.

#### **C. Performance and Feedback (Frontend)**

* **Interface States:** The **SPA** uses **skeleton screens** to indicate batch processing progress and duplicate verification status in the backend.

* **Real-Time Updates:** The frontend uses **asynchronous HTTP calls** to update dataset counters and jurimetrics dashboards once the **Bulk Create** is confirmed by the server, ensuring users see database growth without page reload.

---

**Backend Flow Mapping:**

1. **Request:** Fetch 50 records per topic from DataJud.
2. **Adapter:** Normalize JSON to the `LaborCase` interface.
3. **Filter:** `get_non_existent(api_list)` → returns only new IDs.
4. **Bulk Create:** Saves new cases in a single transaction.

Would you like help defining a unified Adapter interface to ensure fields like "Moral Damage Compensation" map consistently across sources?
