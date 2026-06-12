# PawKart: Real-Time Inventory Synchronization and Intelligent Replenishment for Independent Pet Stores Competing in Quick-Commerce Environments

**Araly Akanksha Naidu** (Dept. of MSc. Big Data Analytics, 252BDA32)  
**Betty K** (Dept. of MCA, 253MCA49)  
**Anna Jose** (Dept. of MCA, 253MCA55)  
**Amrutha M** (Dept. of MCA, 253MCA23)  
**Yeshwanth Kumar H** (Dept. of MSc. Big Data Analytics, 252BDA23)  

---

## Abstract
The rise of quick-commerce platforms has drastically redefined urban retail expectations, with consumers demanding real-time inventory visibility and sub-30-minute delivery. Independent pet stores, catering to a fast-growing but specialized demographic, struggle to meet these demands due to legacy inventory systems and manual operations. While existing solutions explore AI-driven demand prediction and specialized logistics independently, few address the holistic operational requirements of independent, resource-constrained pet retailers. 

This paper proposes an integrated, intelligent retail framework combining real-time event-driven messaging infrastructure, Temporal Fusion Transformers (TFT) for advanced demand forecasting, CatBoost for customer behavior prediction, and XGBoost for personalized product recommendations. Paired with a multi-agent reinforcement learning approach for replenishment optimization and automated last-mile delivery coordination, the system bridges the gap between enterprise-grade quick-commerce capabilities and small-scale specialty retail. 

Designed for non-technical operators, the framework includes an explainability layer utilizing SHAP values. Empirical evaluations against a simulated manual baseline reveal significant improvements in inventory accuracy, stockout frequency, and order fulfillment time. The findings indicate that independent pet stores can leverage commodity cloud infrastructure and state-of-the-art open-source machine learning models to achieve the operational velocity of enterprise quick-commerce networks.

**Keywords:** Artificial Intelligence (AI), Temporal Fusion Transformers (TFT), Omnichannel Retailing, Inventory Management, Demand Forecasting, Quick Commerce, Reinforcement Learning, CatBoost, XGBoost.

---

## 1. Introduction
The quick-commerce paradigm has shifted urban retail from a channel-focused model to a velocity-focused one. Customers now expect real-time stock visibility and immediate deliveries. For independent pet stores, this shift is critical due to the high-urgency nature of pet care purchases, specialized diets, and brand loyalty. However, these retailers typically operate with minimal digital infrastructure, relying on manual batch updates that create delays, data inconsistencies, and stock visibility errors.

Contemporary retail research emphasizes that physical stores must operate simultaneously as sales floors and fulfillment nodes. Achieving this requires instantaneous coordination across inventory, order routing, and delivery systems. This paper presents an AI-driven, omnichannel inventory framework tailored for independent pet retailers. By transitioning from legacy models to a modern stack utilizing Temporal Fusion Transformers (TFT), CatBoost, and XGBoost algorithms integrated with event-driven architecture, small-to-medium businesses can match the responsiveness of enterprise-level digital platforms.

## 2. Literature Review
In omnichannel retailing, competitiveness relies heavily on processing real-time inventory information to drive responsive replenishment. Research on quick-commerce network design highlights that customer proximity and tightly coordinated logistics are essential for sub-30-minute deliveries. While enterprise retailers optimize this through decentralized fulfillment centers, independent retailers are constrained by fragmented inventory tracking.

Event-driven retail architectures have proven effective in mitigating stockout frequencies and cross-channel discrepancies. Furthermore, predictive inventory intelligence using machine learning models significantly improves replenishment timing and safety-stock management. While earlier studies focused on simple moving averages or basic neural networks like LSTMs for forecasting, modern literature points toward attention-based architectures such as Temporal Fusion Transformers (TFT) for handling multi-horizon forecasting with complex temporal dynamics. Despite these advances, practical integration frameworks tailored for independent specialty retailers remain underexplored. This study addresses the gap by integrating state-of-the-art predictive algorithms with practical, event-driven infrastructure.

## 3. Problem Statement
Independent pet stores in urban centers face intense competition from quick-commerce giants. Relying on disconnected legacy systems, these independent retailers suffer from poor inventory visibility, chronic stockouts of fast-moving products, and delayed fulfillment. Existing quick-commerce solutions are engineered for enterprise architectures with substantial capital, making them inaccessible to small businesses. There is a critical need for an accessible, AI-driven framework that provides independent pet retailers with predictive inventory capabilities, real-time synchronization, and hyperlocal delivery integration.

## 4. Objectives
**Main Objective:** To engineer an AI-driven, event-based predictive inventory and quick-commerce fulfillment framework tailored for independent pet stores to enhance real-time stock visibility, minimize inconsistencies, and expedite hyperlocal delivery.

**Specific Objectives:**
1. Develop an event-driven architecture for continuous inventory synchronization across branches.
2. Implement Temporal Fusion Transformers (TFT) to accurately forecast multi-horizon product demand.
3. Utilize CatBoost and XGBoost to model customer behavior and generate real-time product recommendations.
4. Design a dynamic reinforcement-learning-based reorder mechanism to optimize stock levels and automate replenishment.
5. Integrate automated hyperlocal delivery routing to achieve sub-30-minute fulfillment.
6. Evaluate the system's operational impact through rigorous simulation metrics.

## 5. Methodology
### 5.1. System Architecture
The framework employs an independently deployable microservices architecture designed for 99.99% availability. It adheres to event sourcing and Command Query Responsibility Segregation (CQRS) principles.

### 5.2. Event Bus and Messaging Infrastructure
Apache Kafka (or AWS Kinesis) acts as the primary event bus. Every transaction, stock adjustment, or transfer is recorded as an immutable event. Read models are generated separately, guaranteeing high-throughput, low-latency updates across all store locations.

### 5.3. Machine Learning Core
The intelligence layer replaces legacy LSTM architectures with three highly specialized, state-of-the-art sub-systems:
- **Demand Forecasting (TFT):** A Temporal Fusion Transformer model predicts multi-horizon demand. TFTs excel at combining static metadata (product categories) with time-varying known inputs (day-of-week) and historical sales sequences, offering superior accuracy over traditional recurrent models.
- **Customer Prediction (CatBoost):** A gradient boosting model (CatBoost) predicts customer purchase probability and churn, natively handling categorical features without extensive preprocessing.
- **Recommendations (XGBoost):** An XGBoost-based recommendation engine dynamically generates substitute product suggestions and cross-selling opportunities based on historical transaction affinities.

### 5.4. Inventory Execution and Delivery
Replenishment operates via a multi-agent reinforcement learning (MARL) layer that balances stockout risks against overstock penalties across the entire store network. Automated delivery coordination interfaces with hyperlocal logistics providers to dispatch orders based on distance and priority logic.

## 6. Implementation
### 6.1. Technology Stack
The backend is powered by Python and FastAPI to ensure high-performance, asynchronous REST API serving. The frontend utilizes React.js for an adaptive store-owner dashboard. PostgreSQL serves as the relational ledger, while Redis provides an ultra-fast caching layer for real-time stock readings. The ML stack leverages TensorFlow for TFT, alongside the CatBoost and XGBoost libraries for tabular predictions. 

### 6.2. Dataset and Feature Engineering
A synthetic dataset modeled on Bengaluru pet store dynamics was constructed, encompassing 120 SKUs over 12 months. Features included 14-day rolling volumes, perishability indices, and categorical tags. The TFT model leveraged these along with static covariates (brand, category) to predict the subsequent 7-day demand horizon.

### 6.3. Explainability Layer
To ensure trust among non-technical store operators, SHAP (SHapley Additive exPlanations) values are computed for predictions. The dashboard surfaces plain-language rationales for every automated reorder and delivery routing decision, maintaining human-in-the-loop oversight.

## 7. Results
### 7.1. Inventory Accuracy and Stockouts
Across the simulated evaluation, system-reported inventory accuracy reached 97.3%, compared to the 81.6% baseline of manual systems. Crucially, the daily stockout rate dropped from 12.4% to just 2.1% — an 83.1% relative reduction. The most dramatic improvements were observed in critical categories like prescription diets and veterinary supplements.

### 7.2. Forecasting Precision
The adoption of Temporal Fusion Transformers yielded an overall Mean Absolute Percentage Error (MAPE) of 8.1%, outperforming both historical baselines (ARIMA at 14.2%) and legacy LSTM architectures previously evaluated. TFT effectively handled sudden temporal shifts and accurately isolated seasonal spikes.

### 7.3. Fulfillment Velocity
Pre-dispatch latency was reduced from an average of 18.4 minutes to just 4.7 minutes through automated stock verification and pick-list generation. Consequently, 78.4% of orders within a 3km radius were successfully handed off to delivery partners to meet the sub-30-minute delivery threshold.

## 8. Analysis and Discussion
The results substantiate that the technology gap facing independent specialty retailers can be closed utilizing open-source infrastructure. The transition from legacy LSTMs to Temporal Fusion Transformers, combined with CatBoost and XGBoost, provides enterprise-grade predictive accuracy at a fraction of the computational overhead. The significant reduction in stockouts of high-urgency items directly correlates with customer retention in the competitive pet care sector. 

## 9. Conclusion
PawKart demonstrates that independent pet retailers can successfully transition to quick-commerce operational models without requiring enterprise-scale capital. By integrating event-driven architecture with a modern AI stack (TFT, CatBoost, XGBoost), the proposed framework achieved 97.3% inventory accuracy and sub-30-minute fulfillment for the vast majority of local orders. The system establishes a scalable, domain-agnostic blueprint for empowering small-to-medium specialty retailers.

## 10. Future Scope
1. **Live Field Deployment:** Transitioning from simulated environments to live, longitudinal studies in active Bengaluru pet stores to assess physical hardware integration (RFID edge cases) and real-world UI/UX efficacy.
2. **External Data Integration:** Enhancing the TFT forecasting model by integrating hyperlocal weather data, public holiday scraping, and localized social media trend signals to better predict high-volatility SKUs.
3. **Advanced Generative AI Interfaces:** Expanding the Explainable AI layer with a Large Language Model (LLM) copilot, allowing store owners to query inventory health and receive strategic recommendations via natural language conversations.
4. **Automated Order Splitting:** Implementing partial fulfillment logic where multi-SKU orders lacking inventory at a single branch are automatically split and sourced from adjacent branches to drive the sub-30-minute fulfillment rate above 95%.
5. **Cross-Vertical Generalization:** Adapting the feature engineering pipelines and multi-agent reinforcement learning topologies to serve other specialized, urgency-driven retail sectors, such as independent pharmacies and organic grocers.

## 11. Acknowledgements
We express our gratitude to the Department of Master of Computer Applications and the Department of M.Sc. Big Data Analytics at St. Joseph's University, Bengaluru, for their academic support. We acknowledge the ERA Foundation India and ComedKares for their institutional recognition. All software libraries utilized in this research are open-source.

## References
[1] Y. Chen, S. Cheung, and S. Tan, "Stockout and retail logistics: The impact of inventory accuracy on service levels," *Int. J. Production Economics*, vol. 228, 2020.  
[2] N. DeHoratius and A. Raman, "Inventory record inaccuracy: An empirical analysis," *Management Science*, vol. 54, no. 4, 2008.  
[3] X. Li, Q. Li, and X. Chen, "Deep learning for demand forecasting in retail supply chains," *Expert Systems with Applications*, vol. 165, 2021.  
[4] B. Lim, S. O. Arik, N. Loeff, and T. Pfister, "Temporal Fusion Transformers for interpretable multi-horizon time series forecasting," *Int. J. Forecasting*, vol. 37, no. 4, 2021.  
[5] L. Prokhorenkova, G. Gusev, A. Vorobev, A. V. Dorenko, and A. Gulin, "CatBoost: unbiased boosting with categorical features," *Advances in Neural Information Processing Systems*, 2018.  
[6] T. Chen and C. Guestrin, "XGBoost: A Scalable Tree Boosting System," *Proceedings of the 22nd ACM SIGKDD Int. Conf. on Knowledge Discovery and Data Mining*, 2016.  
[7] J. Schulman et al., "Proximal policy optimization algorithms," *arXiv preprint arXiv:1707.06347*, 2017.  
[8] S. M. Lundberg and S.-I. Lee, "A unified approach to interpreting model predictions," *NeurIPS*, 2017.  
[9] Apache Software Foundation, "Apache Kafka," 2024. [Online]. Available: https://kafka.apache.org  
[10] H. Yang, S. Oprea, and L. Liu, "Fulfillment center network planning for quick commerce," *Transportation Research Part E*, vol. 167, 2022.  
