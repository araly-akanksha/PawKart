<img width="650" height="92" alt="image" src="https://github.com/user-attachments/assets/f2df4436-8bd8-45a7-83b8-e2cbbf1e0bcd" />

# PawKart: Real-Time Inventory Synchronization and Intelligent Replenishment for Independent Pet Stores Competing in Quick-Commerce Environments

**Araly Akanksha Naidu** (Dept. of MSc. Big Data Analytics, 252BDA32)  
**Betty K** (Dept. of MCA, 253MCA49)  
**Anna Jose** (Dept. of MCA, 253MCA55)  
**Amrutha M** (Dept. of MCA, 253MCA23)  
**Yeshwanth Kumar H** (Dept. of MSc. Big Data Analytics, 252BDA23)  

---

## Abstract
The rise of quick-commerce platforms has drastically redefined urban retail expectations, with consumers demanding real-time inventory visibility and sub-30-minute delivery. Independent pet stores, catering to a fast-growing but specialized demographic, struggle to meet these demands due to legacy inventory systems, manual operations, and fragmented data architectures. While existing solutions explore AI-driven demand prediction and specialized logistics independently, few address the holistic operational requirements of independent, resource-constrained pet retailers. 

This paper proposes an integrated, intelligent retail framework combining high-performance RESTful/WebSocket communication, advanced machine learning, and structured data pipelines to bridge the operational gap between enterprise-grade quick-commerce networks and small-scale specialty retail. We detail the implementation of a modern, multi-model AI stack utilizing **Temporal Fusion Transformers (TFT)** for accurate, multi-horizon demand forecasting; **CatBoost** for predictive customer behavior and churn analysis; and **XGBoost** for dynamic, personalized product recommendations. 

Designed specifically for non-technical operators, the framework includes an intuitive React-based dashboard layer and a Python FastAPI backend, augmented by an explainability layer utilizing SHAP values to build trust in algorithmic decision-making. Empirical evaluations against a simulated manual baseline reveal significant improvements in inventory accuracy, stockout frequency, and order fulfillment time. 

Crucially, this paper establishes a realistic boundary between the implemented capabilities and future enterprise scaling. While our current implementation successfully deploys advanced predictive models and real-time synchronization, we outline a comprehensive roadmap for future work, including the integration of Multi-Agent Reinforcement Learning (MARL) for automated reordering, Apache Kafka for distributed event streaming, and physical RFID IoT sensing networks. The findings indicate that independent pet stores can leverage commodity cloud infrastructure and state-of-the-art open-source machine learning to immediately achieve operational velocity, while steadily maturing toward a fully autonomous quick-commerce ecosystem.

**Keywords:** Artificial Intelligence (AI), Temporal Fusion Transformers (TFT), Omnichannel Retailing, CatBoost, XGBoost, Inventory Management, Demand Forecasting, Quick Commerce, Real-Time Synchronization.

---

## 1. Introduction
The quick-commerce paradigm has shifted urban retail from a channel-focused model to a velocity-focused one. Customers now expect real-time stock visibility and immediate deliveries within 10 to 30 minutes. For independent pet stores, this shift is critical due to the high-urgency nature of pet care purchases—such as specific prescription diets, specialized supplements, and brand-loyal consumables. However, these retailers typically operate with minimal digital infrastructure, relying on manual batch updates, handwritten ledgers, or disjointed point-of-sale (POS) systems that create delays, data inconsistencies, and chronic stock visibility errors.

Contemporary retail research emphasizes that physical stores must operate simultaneously as sales floors and fulfillment nodes (a concept known as "dark store" hybridity). Achieving this requires instantaneous coordination across inventory, order routing, and delivery systems. When a customer orders a specific 15kg bag of premium dog food, the system must immediately reserve that stock, trigger a local pick-and-pack workflow, calculate remaining stock for future walk-ins, and initiate predictive reordering if safety thresholds are breached. 

This paper presents an AI-driven, omnichannel inventory framework tailored for independent pet retailers, named **PawKart**. By transitioning from rudimentary statistical models to a modern, decoupled machine learning stack utilizing Temporal Fusion Transformers (TFT), CatBoost, and XGBoost algorithms integrated with a high-speed asynchronous backend, small-to-medium businesses can match the responsiveness of enterprise-level digital platforms. This study details our implemented prototype, evaluates its immediate impact on fulfillment velocity and stock accuracy, and explicitly defines the future architectural enhancements required to scale this framework into a fully distributed, autonomous retail network.

---

## 2. Literature Review
The intersection of omnichannel retailing, machine learning, and supply chain logistics forms the theoretical basis of this study. Competitiveness in hyper-local commerce relies heavily on processing real-time inventory information to drive responsive replenishment.

**2.1 Quick-Commerce Network Design**
Research on quick-commerce highlights that customer proximity and tightly coordinated logistics are essential for sub-30-minute deliveries. While enterprise retailers (e.g., Zepto, Blinkit) optimize this through vast networks of decentralized fulfillment centers and distributed event streaming, independent retailers are constrained by a single-store or small-chain footprint, relying on fragmented inventory tracking. Studies show that without real-time synchronization, omnichannel fulfillment attempts lead to a 30-40% increase in canceled orders due to "phantom inventory" (stock that appears available online but is missing from the physical shelf) [1, 2].

**2.2 Predictive Intelligence in Retail**
Predictive inventory intelligence using machine learning models significantly improves replenishment timing and safety-stock management. Early studies focused on simple moving averages (SMA) or Autoregressive Integrated Moving Average (ARIMA) models, which struggle with non-linear sales spikes and complex seasonality. Subsequent research introduced Recurrent Neural Networks (RNNs) and Long Short-Term Memory (LSTM) networks to capture sequential dependencies. However, modern literature points toward attention-based architectures such as **Temporal Fusion Transformers (TFT)** [3]. TFTs are specifically designed for multi-horizon time series forecasting, effectively balancing static metadata (e.g., store location, product category) with time-varying known inputs (e.g., day of the week, upcoming promotions) and historical sales sequences. 

**2.3 Customer Behavior Modeling**
Understanding the customer is as critical as understanding the inventory. Tree-based gradient boosting algorithms have become the industry standard for tabular data in retail. **XGBoost** is widely cited for its speed and scalability in generating personalized recommendations and collaborative filtering [4]. Concurrently, **CatBoost** has emerged as a superior algorithm for handling datasets with high-cardinality categorical features (such as user IDs, product brands, and hyper-local zip codes) without requiring extensive one-hot encoding, making it ideal for predicting customer churn and conversion probabilities [5].

Despite these advances, practical integration frameworks tailored for independent specialty retailers remain underexplored. This study addresses this gap by implementing these state-of-the-art predictive algorithms within a practical, accessible architecture.

---

## 3. Problem Statement
Independent pet stores in urban centers face intense, existential competition from venture-backed quick-commerce giants. Relying on disconnected legacy systems, these independent retailers suffer from three core operational failures:
1. **Poor Inventory Visibility:** Manual tracking leads to a high frequency of "phantom inventory," resulting in canceled online orders and frustrated in-store customers.
2. **Suboptimal Forecasting:** Relying on human intuition or basic moving averages leads to chronic stockouts of fast-moving, high-margin products (e.g., specialized veterinary diets) and costly overstocking of slow-moving accessories.
3. **Delayed Fulfillment:** Without an automated system to route orders, generate pick-lists, and track hyperlocal delivery drivers, independent stores cannot achieve the sub-30-minute delivery promise expected by modern consumers.

Existing quick-commerce enterprise software solutions are prohibitively expensive and require advanced technical teams to maintain. There is a critical need for an accessible, AI-driven framework that provides independent pet retailers with predictive inventory capabilities, real-time synchronization, and intelligent recommendations out-of-the-box.

---

## 4. Objectives

**4.1 Main Objective**  
To engineer and deploy an AI-driven, real-time predictive inventory and quick-commerce fulfillment framework tailored for independent pet stores to enhance stock visibility, minimize inconsistencies, and expedite hyperlocal delivery.

**4.2 Specific Objectives**
1. **Real-Time Synchronization:** Develop a high-speed, asynchronous backend architecture to continuously synchronize inventory, orders, and customer data across multiple store branches.
2. **Advanced Demand Forecasting:** Implement Temporal Fusion Transformers (TFT) to accurately forecast multi-horizon product demand, outperforming traditional LSTM and ARIMA baselines.
3. **Intelligent Customer Modeling:** Utilize CatBoost to model customer behavior, predict churn, and calculate purchase probabilities natively using categorical retail data.
4. **Personalized Recommendations:** Deploy XGBoost to dynamically generate substitute product suggestions and cross-selling opportunities based on historical transaction affinities.
5. **Human-in-the-Loop Explainability:** Integrate SHAP value visualizations into an intuitive React.js dashboard so non-technical store owners can trust and verify AI-driven recommendations.
6. **Establish a Future Roadmap:** Clearly delineate the implemented prototype from future scaling requirements, laying the groundwork for IoT sensor integration and Multi-Agent Reinforcement Learning (MARL).

---

## 5. Methodology and Implemented Architecture

The PawKart framework eschews monolithic legacy designs in favor of an independently deployable microservices architecture. Our currently implemented prototype relies on a robust REST/WebSocket data pipeline, separating transactional workloads from analytical machine learning inferences.

### 5.1 Data Layer and Backend Architecture
The core backend is engineered using **Python and FastAPI**, selected for its native asynchronous capabilities and low-latency request handling. 
- **Relational Ledger:** **PostgreSQL** serves as the primary transactional database, maintaining absolute consistency for purchase orders, supplier data, and customer ledgers using strict ACID compliance.
- **In-Memory Caching:** To prevent database bottlenecking during high-frequency inventory checks, **Redis** is utilized as an ultra-fast caching layer, serving real-time stock readings to the frontend dashboard.

### 5.2 The Machine Learning Core
The intelligence layer replaces rudimentary statistical models and legacy LSTMs with three highly specialized, state-of-the-art sub-systems:

**A. Demand Forecasting via Temporal Fusion Transformers (TFT)**  
TFTs employ a specialized multi-head attention mechanism to identify complex temporal patterns. Unlike basic LSTMs, our TFT model digests three distinct types of inputs:
1. *Static Covariates:* Product category, brand, and item perishability index.
2. *Historical Time-Varying Inputs:* Past 14-day rolling sales volumes and localized volatility metrics.
3. *Known Future Inputs:* Day of the week, upcoming holidays, and scheduled promotional events.
This allows the system to generate highly accurate 7-day forward-looking demand curves.

**B. Customer Behavior Prediction via CatBoost**  
To analyze customer loyalty, we implemented CatBoost. Pet retail data is heavily categorical (e.g., pet breed, preferred food flavor, localized neighborhood). CatBoost utilizes ordered boosting and oblivious decision trees to process these categorical features natively, eliminating target leakage and providing highly accurate predictions on customer churn probability and lifetime value.

**C. Product Recommendations via XGBoost**  
When a user adds an item to their cart, our XGBoost recommendation engine executes real-time collaborative filtering. By analyzing historical transaction affinities (e.g., customers who buy puppy kibble also frequently buy chew toys and training pads), the system generates dynamic cross-selling suggestions, actively increasing the Average Order Value (AOV).

### 5.3 Explainability Layer (XAI)
To ensure system adoption, the algorithms must not operate as "black boxes." We integrated SHapley Additive exPlanations (SHAP) to interpret model outputs. The React.js frontend surfaces plain-language rationales for predictions. For instance, instead of merely suggesting a reorder, the dashboard states: *"Reorder suggested: TFT model predicts a 25% spike in demand due to the upcoming weekend and historically high correlation with monsoon season flea treatments."*

---

## 6. Experimental Setup and Dataset
Since access to real, high-volume transactional data from independent Bengaluru pet stores is proprietary, we constructed a rigorous synthetic dataset that reflects the granular purchasing dynamics of this retail context. The dataset encompasses 12 months of daily sales across 5 simulated store branches and 120 unique SKUs. 

Product categories include dry food (standard and prescription), wet food, treats, grooming products, and veterinary supplements. We deliberately engineered challenging demand patterns: monsoon-season spikes in anti-tick treatments, festival-period lifts in premium treats, and the low-frequency but high-urgency nature of prescription diet purchases.

The models were trained on an 80/20 train-validation split. The TFT forecasting model was evaluated using Mean Absolute Percentage Error (MAPE) and Root Mean Squared Error (RMSE).

---

## 7. Results and Evaluation

### 7.1 Inventory Accuracy and Stockout Reduction
Upon deploying the high-speed FastAPI and Redis caching architecture, system-reported inventory accuracy reached **97.3%**, compared to the **81.6%** baseline typical of manual, batch-updated systems. 

More importantly, the integration of TFT-driven reorder alerts resulted in a drastic drop in the daily stockout rate—from **12.4% to just 2.1%** (an 83.1% relative reduction). The most profound improvements occurred in high-urgency categories like prescription veterinary diets, where stockouts previously resulted in permanent customer loss.

### 7.2 Forecasting Precision (TFT vs Baseline)
The Temporal Fusion Transformer model significantly outperformed traditional baselines. 
- **Naive Moving Average MAPE:** 19.4%
- **ARIMA Baseline MAPE:** 14.2%
- **Legacy LSTM MAPE:** 10.5%
- **PawKart TFT MAPE:** **8.1%**

The TFT model was exceptionally proficient at isolating complex seasonal spikes and mitigating the noise from sporadic, high-volatility purchases, successfully forecasting demand horizons up to 7 days in advance.

### 7.3 Fulfillment Velocity
In our simulated hyperlocal routing environment, pre-dispatch latency (the time between order placement and a delivery driver receiving the package) was reduced from an average of 18.4 minutes to just **4.7 minutes**. This was achieved by replacing manual stock verification with instant digital pick-lists. Consequently, **78.4% of orders** within a 3km radius were successfully prepared and handed off to delivery partners rapidly enough to confidently meet a sub-30-minute delivery threshold.

---

## 8. Analysis and Discussion
The empirical results substantiate that the operational gap facing independent specialty retailers is technological, not structural. By replacing monolithic legacy software with an agile, microservices-oriented Python backend, independent stores can process high-throughput data in real time. 

Furthermore, the transition to state-of-the-art machine learning (TFT, CatBoost, XGBoost) provides enterprise-grade predictive accuracy at a fraction of the computational and financial overhead. Unlike deep learning models that require massive GPU clusters, these optimized models run efficiently on commodity cloud instances, preserving the profit margins of small businesses. The significant reduction in stockouts of high-urgency items directly correlates with customer retention, proving that intelligent inventory systems are a core driver of retail revenue, not just a back-office tool.

---

## 9. Conclusion
The PawKart prototype successfully demonstrates that independent pet retailers can transition to a quick-commerce operational model without requiring venture-scale capital. By integrating a high-speed React/FastAPI architecture with a modern, multi-model AI stack (Temporal Fusion Transformers, CatBoost, XGBoost), the proposed framework achieved 97.3% inventory accuracy, an 8.1% forecasting MAPE, and sub-30-minute fulfillment preparation for the vast majority of local orders. The system establishes a scalable, domain-agnostic blueprint that empowers small-to-medium specialty retailers to survive and thrive against enterprise quick-commerce competitors.

---

## 10. Future Scope and Work

While the current PawKart implementation successfully modernizes the data pipeline and predictive intelligence layers, achieving a fully autonomous, enterprise-grade retail network requires several advanced architectural enhancements. We have identified the following key areas for future research and development:

**1. Distributed Event Streaming with Apache Kafka**
Currently, the system relies on rapid REST APIs and WebSocket connections. To scale from 5 stores to 500 stores, the architecture must transition to a fully distributed event-driven mesh. Integrating **Apache Kafka (or AWS Kinesis)** as a central event bus will allow every transaction, stock adjustment, or branch transfer to be processed as an immutable, replayable event, ensuring zero data loss and absolute state consistency across a massive geographic footprint.

**2. Multi-Agent Reinforcement Learning (MARL) for Autonomous Replenishment**
Our current prototype utilizes static reorder threshold formulas augmented by TFT forecasts. Future iterations will implement **Multi-Agent Reinforcement Learning**. By modeling the supply chain as a cooperative environment, individual RL agents (representing store branches) will learn to dynamically transfer inventory laterally between branches, balancing system-wide stockout penalties against warehouse overstock costs without human intervention.

**3. Physical IoT and RFID Edge Integration**
The current inventory accuracy relies on rigorous digital point-of-sale scanning. To achieve true 100% real-time visibility, future work includes the deployment of physical **UHF RFID sensors** on store shelving. This IoT integration will automatically detect when a physical item is removed from a shelf by a walk-in customer, broadcasting an immediate MQTT event to the backend, completely eliminating human scanning errors.

**4. External Data Ingestion for High-Volatility Forecasting**
The current 8.1% MAPE can be further minimized by ingesting exogenous variables. Future updates to the TFT model will integrate live data streams from hyperlocal weather APIs, public holiday scrapers, and localized social media sentiment analysis to predict sudden demand shocks (e.g., a sudden thunderstorm causing a spike in indoor training pads).

**5. Generative AI Copilot for Store Managers**
Expanding upon the existing SHAP explainability layer, we propose integrating a Large Language Model (LLM) copilot via Retrieval-Augmented Generation (RAG). This will allow non-technical store managers to interact with their inventory data conversationally, asking queries such as, *"Which dog food brands are at risk of a stockout before Friday?"* and receiving instant, strategic recommendations.

**6. Automated Order Splitting and Dynamic Routing**
Addressing the 21.6% of orders that missed the express fulfillment window requires advanced partial-fulfillment logic. Future algorithms will automatically split multi-SKU orders, dispatching available items immediately from the primary store while seamlessly routing the missing items from an adjacent branch or central warehouse, pushing the sub-30-minute delivery success rate above 95%.

---

## 11. Acknowledgements
We express our sincere gratitude to the Department of Master of Computer Applications and the Department of M.Sc. Big Data Analytics at St. Joseph's University, Bengaluru, for their academic environment and support. We acknowledge the ERA Foundation India and ComedKares for their institutional recognition of student research initiatives. All software libraries utilized in this research (FastAPI, React, TensorFlow, CatBoost, XGBoost) are open-source. This research received no external funding.

---

## References
[1] Y. Chen, S. Cheung, and S. Tan, "Stockout and retail logistics: The impact of inventory accuracy on service levels," *Int. J. Production Economics*, vol. 228, 2020.  
[2] N. DeHoratius and A. Raman, "Inventory record inaccuracy: An empirical analysis," *Management Science*, vol. 54, no. 4, 2008.  
[3] B. Lim, S. O. Arik, N. Loeff, and T. Pfister, "Temporal Fusion Transformers for interpretable multi-horizon time series forecasting," *Int. J. Forecasting*, vol. 37, no. 4, 2021.  
[4] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," *Proceedings of the 22nd ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining*, 2016.  
[5] L. Prokhorenkova, G. Gusev, A. Vorobev, A. V. Dorenko, and A. Gulin, "CatBoost: unbiased boosting with categorical features," *Advances in Neural Information Processing Systems*, 2018.  
[6] X. Li, Q. Li, and X. Chen, "Deep learning for demand forecasting in retail supply chains," *Expert Systems with Applications*, vol. 165, 2021.  
[7] J. Schulman et al., "Proximal policy optimization algorithms," *arXiv preprint arXiv:1707.06347*, 2017.  
[8] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," *NeurIPS*, 2017.  
[9] Apache Software Foundation, "Apache Kafka," 2024. [Online]. Available: https://kafka.apache.org  
[10] H. Yang, S. Oprea, and L. Liu, "Fulfillment center network planning for quick commerce," *Transportation Research Part E*, vol. 167, 2022.
