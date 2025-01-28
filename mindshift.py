# mindshift.py

import streamlit as st
import scr  # We import our separate scr.py module

# Ensure session state for login
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# LOGIN CHECK
if not st.session_state["logged_in"]:
    # Use the login function from scr.py
    scr.login()
else:

    # Streamlit App Title
    st.title("Intelligent Dashboard Analytics")
    st.sidebar.title("MindShift")
    st.sidebar.write("Explore different analyses")
    st.image("mindshift.jpg", width=200)

    # File Upload
    uploaded_file = st.file_uploader("Upload your file (csv, txt, xlsx, xls)", type=["csv", "txt", "xlsx", "xls"])
    if uploaded_file:
        # Load data based on file type
        if uploaded_file.name.endswith(".csv") or uploaded_file.name.endswith(".txt"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        # Convert Date columns to datetime
        data["Date"] = pd.to_datetime(data["Date"], errors='coerce')
        data["CheckInDate"] = pd.to_datetime(data["CheckInDate"], errors='coerce')
        data["CheckOutDate"] = pd.to_datetime(data["CheckOutDate"], errors='coerce')

        # Add Year column for analysis
        if "Date" in data.columns and data["Date"].notna().any():
            data["Year"] = data["Date"].dt.year
        else:
            data["Year"] = 0  # fallback if Date is missing

        # Calculate Rooms Revenue Per Year (including Family Room)
        if "ADR" in data.columns:
            data["SingleRoomRevenue"] = data.get("SingleRoomsOccupied", 0) * data["ADR"]
            data["DoubleRoomRevenue"] = data.get("DoubleRoomsOccupied", 0) * data["ADR"]
            data["RoyalRoomRevenue"] = data.get("RoyalRoomsOccupied", 0) * data["ADR"]
            data["FamilyRoomRevenue"] = data.get("FamilyRoomsOccupied", 0) * data["ADR"]  # Add Family Room
        else:
            # If no ADR column, create placeholders
            data["SingleRoomRevenue"] = 0
            data["DoubleRoomRevenue"] = 0
            data["RoyalRoomRevenue"] = 0
            data["FamilyRoomRevenue"] = 0  # Add Family Room

        # Calculate Room Costs
        unit_prices = {
            "Single Room": 470,
            "Double Room": 680,
            "Family Room": 729,
            "Royal Room": 800
        }
        data["RoomCost"] = (
            data["SingleRoomsOccupied"] * unit_prices["Single Room"] +
            data["DoubleRoomsOccupied"] * unit_prices["Double Room"] +
            data["FamilyRoomsOccupied"] * unit_prices["Family Room"] +
            data["RoyalRoomsOccupied"] * unit_prices["Royal Room"]
        )

        # Calculate Profit
        data["Profit"] = data["TotalRevenue"] - (
            data["RoomCost"] +
            data["UtilityCostElectricity"] +
            data["UtilityCostWater"] +
            data["UtilityCostGas"] +
            data["StaffSalaryHousekeeping"] +
            data["StaffSalaryFrontDesk"] +
            data["StaffSalaryMaintenance"] +
            data["StaffSalaryF&B"] +
            data["StaffSalaryMarketing"] +
            data["MaintenanceCost"] +
            data["DepreciationCost"] +
            data["MealPlanCost"]
        )

        room_revenue_per_year = (
            data.groupby("Year")[["SingleRoomRevenue", "DoubleRoomRevenue", "RoyalRoomRevenue", "FamilyRoomRevenue"]]
            .sum()
            .reset_index()
            .melt(id_vars=["Year"], var_name="RoomType", value_name="Revenue")
        )

        # ─────────────────────────────────────────────────────────────────────────
        # 1) DYNAMIC FILTERING (Date, Nationality, Loyalty)
        # ─────────────────────────────────────────────────────────────────────────
        st.sidebar.header("Data Filtering")

        # Date Range Filter (only if valid date data is present)
        if "Date" in data.columns and data["Date"].notna().any():
            min_date = data["Date"].min()
            max_date = data["Date"].max()
            start_date = st.sidebar.date_input("Start Date", min_date)
            end_date = st.sidebar.date_input("End Date", max_date)
            mask_date = (data["Date"] >= pd.to_datetime(start_date)) & (data["Date"] <= pd.to_datetime(end_date))
        else:
            mask_date = pd.Series([True]*len(data))

        # Nationality Filter
        if "Nationality" in data.columns:
            unique_nat = data["Nationality"].dropna().unique()
            selected_nat = st.sidebar.multiselect("Select Nationalities", options=unique_nat, default=unique_nat)
            mask_nat = data["Nationality"].isin(selected_nat)
        else:
            mask_nat = pd.Series([True]*len(data))

        # Loyalty Tier Filter
        if "LoyaltyTier" in data.columns:
            unique_loyalty = data["LoyaltyTier"].dropna().unique()
            selected_loyalty = st.sidebar.multiselect("Select Loyalty Tiers", options=unique_loyalty, default=unique_loyalty)
            mask_loyalty = data["LoyaltyTier"].isin(selected_loyalty)
        else:
            mask_loyalty = pd.Series([True]*len(data))

        # Combine all filters
        filtered_data = data[mask_date & mask_nat & mask_loyalty]

        # Navigation Options
        options = [
            "Overview",
            "Revenue Analysis",
            "Guest Analysis",
            "Seasonality",
            "Housekeeping & Laundry",
            "Feedback Analysis",
            "Custom Charts",
            "KPIs",
            "Advanced Analysis",
            "Cancellation & No-Show Analysis",
            "Guest Retention & Repeat Visits",
            "Marketing ROI & Campaign Performance",
            "Operational Efficiency & Resource Allocation",
            "Room Type Profitability Analysis",
            "CLTV Estimation",
            "Upselling & Cross-Selling",
            "Room Cost Analysis",  # New option for Room Cost Analysis
            "Dynamic Pricing Suggestions",  # New option for Dynamic Pricing Suggestions
            "Guest Preferences",  # New option for Guest Preferences
            "Scenario Planning",  # New option for Scenario Planning
            "Story Telling",  # <--- NEW
            "Dig Deeper",
            "Company's"# <--- NEW
        ]
        choice = st.sidebar.radio("Select a category", options)

        # ─────────────────────────────────────────────────────────────────────────
        #  DASHBOARD SECTIONS
        # ─────────────────────────────────────────────────────────────────────────

        # ----------------------------- OVERVIEW --------------------------------
        if choice == "Overview":
            st.header("Overview of the Dataset")
            st.dataframe(filtered_data.head(10))
            st.write("**Dataset Statistics (Filtered)**")
            st.write(filtered_data.describe())

        # ------------------------- REVENUE ANALYSIS ----------------------------
        elif choice == "Revenue Analysis":
            st.header("Revenue Analysis")
            if "TotalRevenue" in filtered_data.columns:
                st.write(f"**Total Revenue (Filtered):** ${filtered_data['TotalRevenue'].sum():,.2f}")
            else:
                st.write("**TotalRevenue column is not available in the data.**")

            # Weekly Revenue
            if "Date" in filtered_data.columns and "TotalRevenue" in filtered_data.columns:
                weekly_revenue = (
                    filtered_data
                    .groupby(filtered_data["Date"].dt.to_period("W").astype(str))["TotalRevenue"]
                    .sum()
                    .reset_index()
                )
                weekly_revenue.columns = ["Week", "TotalRevenue"]
                if not weekly_revenue.empty:
                    selected_week = st.selectbox("Select a Week", weekly_revenue["Week"])
                    selected_week_data = weekly_revenue[weekly_revenue["Week"] == selected_week]
                    revenue_value = selected_week_data["TotalRevenue"].values[0]
                    st.write(f"**Weekly Revenue for {selected_week}:** ${revenue_value:,.2f}")

                    fig_weekly = px.line(
                        weekly_revenue, x="Week", y="TotalRevenue", 
                        title="Weekly Revenue (Filtered)", markers=True
                    )
                    st.plotly_chart(fig_weekly)
                    with st.expander("Explain Weekly Revenue"):
                        st.markdown("""
                        **Weekly Revenue** shows how total revenue fluctuates each week within the filtered range.
                        This helps identify periods of higher or lower demand, which can inform pricing or
                        marketing decisions for those weeks.
                        """)
                        # Arabic explanation
                        st.markdown("""
                        **الإيرادات الأسبوعية** تُظهر كيف تتغير الإيرادات الإجمالية كل أسبوع ضمن النطاق المحدد.
                        يساعد ذلك في تحديد الفترات ذات الطلب الأعلى أو الأقل، مما يمكن أن يوجّه قرارات التسعير
                        أو التسويق لتلك الأسابيع.
                        """)
                else:
                    st.write("No data available for weekly revenue with current filters.")

            # ADR vs Total Revenue
            if "ADR" in filtered_data.columns and "TotalRevenue" in filtered_data.columns:
                st.write("**Relationship Between ADR and Total Revenue** (Filtered)")
                fig_adr = px.scatter(
                    filtered_data, x="ADR", y="TotalRevenue", 
                    trendline="ols", title="ADR vs Total Revenue"
                )
                st.plotly_chart(fig_adr)
                with st.expander("Explain ADR vs Total Revenue"):
                    st.markdown("""
                    This chart shows how changes in Average Daily Rate (ADR) affect total revenue.
                    A positive correlation suggests that higher room prices may lead to higher total revenue.
                    However, occupancy and other factors also play important roles.
                    """)
                    st.markdown("""
                    **يُظهر هذا الرسم البياني كيف تؤثر التغييرات في متوسط السعر اليومي (ADR) على إجمالي الإيرادات.
                    يشير الارتباط الإيجابي إلى أن ارتفاع أسعار الغرف قد يؤدي إلى زيادة إجمالي الإيرادات.
                    ومع ذلك، فإن معدل الإشغال والعوامل الأخرى تلعب أيضًا أدوارًا مهمة.
                    """)

            # Marketing Spend vs Total Revenue
            if "MarketingSpend" in filtered_data.columns and "TotalRevenue" in filtered_data.columns:
                st.write("**Relationship Between Marketing Spend and Total Revenue** (Filtered)")
                fig_mktg = px.scatter(
                    filtered_data, x="MarketingSpend", y="TotalRevenue",
                    trendline="ols", title="Marketing Spend vs Total Revenue"
                )
                st.plotly_chart(fig_mktg)
                with st.expander("Explain Marketing Spend vs Total Revenue"):
                    st.markdown("""
                    This chart highlights how your marketing budget correlates with total revenue.
                    A strong correlation would suggest your marketing campaigns are effective at driving revenue.
                    If it's weak, you may need to adjust your marketing strategy or targeting.
                    """)
                    st.markdown("""
                    **يُظهر هذا الرسم البياني كيف ترتبط ميزانيتك التسويقية بإجمالي الإيرادات.**
                    **يشير الارتباط القوي إلى أن حملاتك التسويقية فعالة في زيادة الإيرادات.**
                    **إذا كان الارتباط ضعيفًا، فقد تحتاج إلى تعديل استراتيجية التسويق أو استهداف الجمهور.**
                    """)

            # Rooms Revenue per Year (including Family Room)
            st.write("**Rooms Revenue per Year**")
            filtered_room_revenue_per_year = (
                filtered_data
                .groupby("Year")[["SingleRoomRevenue", "DoubleRoomRevenue", "RoyalRoomRevenue", "FamilyRoomRevenue"]]
                .sum()
                .reset_index()
                .melt(id_vars=["Year"], var_name="RoomType", value_name="Revenue")
            )
            if not filtered_room_revenue_per_year.empty:
                fig_rooms = px.bar(
                    filtered_room_revenue_per_year, 
                    x="Year", y="Revenue", color="RoomType", 
                    barmode="group", title="Rooms Revenue by Year"
                )
                st.plotly_chart(fig_rooms)
                with st.expander("Explain Rooms Revenue by Year"):
                    st.markdown("""
                    This compares revenue from Single, Double, Royal, and Family rooms over different years.
                    It helps you see which type of room generates the most revenue and how it changes yearly.
                    """)
                    st.markdown("""
                    يقارن هذا الرسم البياني الإيرادات من الغرف الفردية والمزدوجة والغرف الملكية والعائلية على مدار سنوات مختلفة.
                    يساعدك على رؤية نوع الغرفة الذي يحقق أكبر إيرادات وكيف يتغير سنويًا.
                    """)
            else:
                st.write("No room revenue data available under the current filters.")

        # ------------------------- GUEST ANALYSIS ------------------------------
        elif choice == "Guest Analysis":
            st.header("Guest Analysis")

            # Nationality Distribution
            if "Nationality" in filtered_data.columns:
                st.subheader("Nationality Distribution")
                nationality_counts = filtered_data["Nationality"].value_counts().reset_index()
                nationality_counts.columns = ["Nationality", "Count"]
                if not nationality_counts.empty:
                    fig_nat = px.pie(
                        nationality_counts, names="Nationality", values="Count",
                        title="Guest Nationality Breakdown"
                    )
                    st.plotly_chart(fig_nat)
                    with st.expander("Explain Nationality Breakdown"):
                        st.markdown("""
                        This pie chart shows the proportion of guests coming from each nationality.
                        Large slices indicate key markets you can target for specialized services or promotions.
                        """)
                        st.markdown("""
                        يُظهر هذا الرسم البياني الدائري نسبة الضيوف القادمين من كل جنسية.
                        تشير الشرائح الكبيرة إلى الأسواق الرئيسية التي يمكنك استهدافها بخدمات أو عروض ترويجية مخصصة.
                        """)
                else:
                    st.write("No nationality data available under the current filters.")

            # Age Group Distribution
            if "AgeGroup" in filtered_data.columns:
                st.subheader("Age Group Distribution")
                age_counts = filtered_data["AgeGroup"].value_counts().reset_index()
                age_counts.columns = ["AgeGroup", "Count"]
                if not age_counts.empty:
                    fig_age = px.bar(
                        age_counts, x="AgeGroup", y="Count", 
                        title="Guest Age Group Distribution"
                    )
                    st.plotly_chart(fig_age)
                    with st.expander("Explain Age Group Distribution"):
                        st.markdown("""
                        This bar chart shows the number of guests in each age group, indicating
                        which age segment is most common. You can use this information for tailored amenities.
                        """)
                        st.markdown("""
                        يُظهر هذا الرسم البياني العمودي عدد الضيوف في كل فئة عمرية، مما يشير إلى
                        أي شريحة عمرية هي الأكثر شيوعًا. يمكنك استخدام هذه المعلومات لتوفير وسائل راحة مخصصة.
                        """)
                else:
                    st.write("No age group data available under the current filters.")

            # Loyalty Tier Analysis
            if "LoyaltyTier" in filtered_data.columns:
                st.subheader("Loyalty Tier Analysis")
                loyalty_counts = filtered_data["LoyaltyTier"].value_counts().reset_index()
                loyalty_counts.columns = ["LoyaltyTier", "Count"]
                if not loyalty_counts.empty:
                    fig_loyalty = px.bar(
                        loyalty_counts, x="LoyaltyTier", y="Count", 
                        title="Loyalty Tier Distribution"
                    )
                    st.plotly_chart(fig_loyalty)
                    with st.expander("Explain Loyalty Tier Distribution"):
                        st.markdown("""
                        This chart shows how many guests fall into each loyalty tier.
                        If you have a large number of top-tier members, consider special offers to keep them engaged.
                        """)
                        st.markdown("""
                        يُظهر هذا الرسم البياني عدد الضيوف في كل مستوى ولاء.
                        إذا كان لديك عدد كبير من الأعضاء في المستوى الأعلى، ففكر في تقديم عروض خاصة لإبقائهم متفاعلين.
                        """)
                else:
                    st.write("No loyalty tier data available under the current filters.")

        # -------------------------- SEASONALITY --------------------------------
        elif choice == "Seasonality":
            st.header("Seasonality Analysis")
            if "Date" in filtered_data.columns and filtered_data["Date"].notna().any():
                if "Month" not in filtered_data.columns:
                    filtered_data["Month"] = filtered_data["Date"].dt.month_name()

                if "TotalRevenue" in filtered_data.columns:
                    monthly_revenue = (
                        filtered_data.groupby("Month")["TotalRevenue"].sum().reset_index()
                    )
                    if not monthly_revenue.empty:
                        fig_month = px.line(
                            monthly_revenue, x="Month", y="TotalRevenue", 
                            title="Monthly Revenue Trend (Filtered)", markers=True
                        )
                        st.plotly_chart(fig_month)

                        # Task 1: Seasonality Analysis with Months and Years
                        st.subheader("Seasonality Analysis with Months and Years")
                        monthly_revenue_year = (
                            filtered_data.groupby(["Year", "Month"])["TotalRevenue"].sum().reset_index()
                        )
                        fig_month_year = px.line(
                            monthly_revenue_year, x="Month", y="TotalRevenue", color="Year",
                            title="Monthly Revenue Trend by Year", markers=True
                        )
                        st.plotly_chart(fig_month_year)

                        # Task 2: Explanation of the Peak
                        peak_month = monthly_revenue.loc[monthly_revenue["TotalRevenue"].idxmax()]
                        st.write(f"**Peak Month:** {peak_month['Month']} with Total Revenue of ${peak_month['TotalRevenue']:,.2f}")
                        st.write("**Explanation:** The peak month typically represents the highest demand period, often due to holidays, events, or favorable weather conditions.")

                        # Task 3: Point at the Peak and Write the Month and Total Revenue
                        st.write(f"**Note:** The highest revenue was achieved in **{peak_month['Month']}** with a total revenue of **${peak_month['TotalRevenue']:,.2f}**.")

                        # Task 4: Point at the Lowest Point and Write the Month and Total Revenue
                        lowest_month = monthly_revenue.loc[monthly_revenue["TotalRevenue"].idxmin()]
                        st.write(f"**Note:** The lowest revenue was recorded in **{lowest_month['Month']}** with a total revenue of **${lowest_month['TotalRevenue']:,.2f}**.")

                        with st.expander("Explain Seasonality Trend"):
                            st.markdown("""
                            This line chart shows how revenue changes month-to-month.
                            Noting which months bring in the most or least revenue can guide
                            staffing, pricing, and promotions.
                            """)
                            st.markdown("""
                            يُظهر هذا الرسم البياني الخطي كيفية تغير الإيرادات من شهر لآخر.
                            يمكن أن تساعدك ملاحظة الأشهر التي تحقق أعلى أو أقل إيرادات في توجيه
                            التوظيف والتسعير والعروض الترويجية.
                            """)
                    else:
                        st.write("No monthly revenue data available for current filters.")
                else:
                    st.write("**TotalRevenue column is not available in the data.**")
            else:
                st.write("Invalid or missing Date column, seasonality analysis not possible.")

        # --------------------- HOUSEKEEPING & LAUNDRY --------------------------
        elif choice == "Housekeeping & Laundry":
            st.header("Housekeeping & Laundry Analysis")

            # Housekeeping Over Time
            if "HousekeepingExpenses" in filtered_data.columns:
                housekeeping_data = (
                    filtered_data
                    .groupby(filtered_data["Date"].dt.to_period("M").astype(str))["HousekeepingExpenses"]
                    .sum()
                    .reset_index()
                )
                housekeeping_data.rename(columns={"Date": "Month"}, inplace=True)
                if not housekeeping_data.empty:
                    fig_hk = px.line(
                        housekeeping_data, 
                        x="Month", 
                        y="HousekeepingExpenses",
                        title="Monthly Housekeeping Expenses",
                        markers=True
                    )
                    st.plotly_chart(fig_hk)
                    with st.expander("Explain Housekeeping Expenses"):
                        st.markdown("""
                        This line chart helps identify patterns or spikes in Housekeeping Expenses.
                        Sudden jumps might need investigation, while stable expenses suggest
                        consistent operations.
                        """)
                        st.markdown("""
                        يساعد هذا الرسم البياني الخطي في تحديد الأنماط أو الارتفاعات المفاجئة في مصروفات النظافة.
                        قد تحتاج الارتفاعات المفاجئة إلى التحقيق، بينما تشير المصروفات المستقرة إلى
                        عمليات ثابتة.
                        """)
                else:
                    st.write("No housekeeping expense data under the current filters.")

            # Laundry Revenue vs. Expenses
            if "LaundryRevenue" in filtered_data.columns and "LaundryExpenses" in filtered_data.columns:
                laundry_data = (
                    filtered_data
                    .groupby(filtered_data["Date"].dt.to_period("M").astype(str))[
                        ["LaundryRevenue", "LaundryExpenses"]
                    ]
                    .sum()
                    .reset_index()
                )
                laundry_data.rename(columns={"Date": "Month"}, inplace=True)
                if not laundry_data.empty:
                    fig_laundry = px.bar(
                        laundry_data, 
                        x="Month", 
                        y=["LaundryRevenue", "LaundryExpenses"], 
                        barmode="group", 
                        title="Laundry Revenue vs. Expenses"
                    )
                    st.plotly_chart(fig_laundry)
                    with st.expander("Explain Laundry Revenue vs. Expenses"):
                        st.markdown("""
                        This bar chart compares revenue from laundry services with the related expenses.
                        If expenses consistently exceed revenue, it may be time to optimize operations or pricing.
                        """)
                        st.markdown("""
                        يُقارن هذا الرسم البياني العمودي الإيرادات من خدمات الغسيل مع المصروفات ذات الصلة.
                        إذا كانت المصروفات تتجاوز الإيرادات باستمرار، فقد يكون الوقت قد حان لتحسين العمليات أو التسعير.
                        """)
                else:
                    st.write("No laundry data available under the current filters.")

        # ------------------------- FEEDBACK ANALYSIS ---------------------------
        elif choice == "Feedback Analysis":
            st.header("Guest Feedback Analysis")
            if "GuestFeedbackScore" in filtered_data.columns and "Date" in filtered_data.columns:
                feedback_monthly = (
                    filtered_data
                    .groupby(filtered_data["Date"].dt.to_period("M").astype(str))["GuestFeedbackScore"]
                    .mean()
                    .reset_index()
                )
                feedback_monthly.rename(columns={"Date": "Month"}, inplace=True)

                if not feedback_monthly.empty:
                    fig_feedback = px.line(
                        feedback_monthly, 
                        x="Month", 
                        y="GuestFeedbackScore", 
                        title="Monthly Average Guest Feedback Score", 
                        markers=True
                    )
                    st.plotly_chart(fig_feedback)
                    with st.expander("Explain Guest Feedback Trends"):
                        st.markdown("""
                        This line chart shows how satisfied guests are over time.
                        Identifying dips in the feedback score can help you investigate
                        any issues guests may be facing and take corrective action.
                        """)
                        st.markdown("""
                        يُظهر هذا الرسم البياني الخطي مدى رضا الضيوف بمرور الوقت.
                        يمكن أن تساعدك تحديد الانخفاضات في تقييم الضيوف في التحقيق
                        في أي مشكلات قد يواجهها الضيوف واتخاذ إجراءات تصحيحية.
                        """)
                else:
                    st.write("No feedback data available under the current filters.")
            else:
                st.write("**GuestFeedbackScore or Date column is missing.**")

        # --------------------------- CUSTOM CHARTS -----------------------------
        elif choice == "Custom Charts":
            st.header("Departments Charts")
            department_columns = [
                "F&B Revenue",
                "Spa Revenue",
                "RestaurantRevenue",
                "MerchandiseRevenue",
                "LaundryRevenue"
            ]
            valid_depts = [col for col in department_columns if col in filtered_data.columns]
            if valid_depts:
                revenue_breakdown = filtered_data[valid_depts].sum().reset_index()
                revenue_breakdown.columns = ["Department", "Revenue"]
                fig_dept = px.bar(
                    revenue_breakdown, 
                    x="Department", 
                    y="Revenue", 
                    title="Revenue Breakdown by Department (Filtered)"
                )
                st.plotly_chart(fig_dept)
                with st.expander("Explain Department Breakdown"):
                    st.markdown("""
                    This bar chart shows how much revenue each department contributes within the filtered data range.
                    It’s useful for seeing which areas bring in the most revenue.
                    """)
                    st.markdown("""
                    يُظهر هذا الرسم البياني العمودي مقدار الإيرادات التي يساهم بها كل قسم ضمن النطاق المحدد.
                    من المفيد رؤية المناطق التي تحقق أكبر إيرادات.
                    """)

        # ------------------------------- KPIs ----------------------------------
        elif choice == "KPIs":
            st.header("Key Performance Indicators (KPIs)")
            # Calculate KPIs only if columns exist
            needed_columns = ["TotalRevenue", "OccupiedRooms", "AvailableRooms", "ADR"]
            if all(col in filtered_data.columns for col in needed_columns):
                total_revenue = filtered_data['TotalRevenue'].sum()
                avg_adr = filtered_data['ADR'].mean()
                occupancy_rate = (
                    filtered_data['OccupiedRooms'].sum() / filtered_data['AvailableRooms'].sum()
                ) * 100

                col1, col2, col3 = st.columns(3)
                col1.metric("Total Revenue", f"${total_revenue:,.2f}")
                col2.metric("Average ADR", f"${avg_adr:,.2f}")
                col3.metric("Occupancy Rate", f"{occupancy_rate:.2f}%")
            else:
                st.write("Required columns for KPIs are missing in the filtered dataset.")

        # ------------------------ ADVANCED ANALYSIS ----------------------------
        elif choice == "Advanced Analysis":
            st.header("Advanced Analysis (Easy Explanations)")

            # Intro
            st.markdown("""
            The **Advanced Analysis** section offers two techniques to better understand your data:
            
            1. **Correlation Heatmap** – A color-coded grid showing which numbers move together.  
            2. **Guest Segmentation (K-Means)** – Grouping similar guests to learn about your audience.

            Even if you’re not a data expert, these tools can help you spot trends and make informed decisions.
            """)

            # 1) Correlation Analysis
            st.subheader("1. Correlation Heatmap (Easy View)")
            st.write("""
            This heatmap shows how different columns relate to each other. 
            - **Red squares** close to +1 mean a strong positive link.  
            - **Blue squares** close to -1 mean a strong negative link.  
            - **White or light colors** near 0 mean little correlation.

            For example, if **ADR** and **TotalRevenue** are strongly correlated,
            that might mean higher room rates increase overall revenue.
            """)
            if st.button("Show Correlation Heatmap"):
                numeric_data = filtered_data.select_dtypes(include=[np.number])
                if not numeric_data.empty:
                    corr = numeric_data.corr()
                    fig_corr = px.imshow(
                        corr, 
                        text_auto=True, 
                        color_continuous_scale='RdBu_r', 
                        origin='lower',
                        title="Correlation Heatmap (Filtered Data)"
                    )
                    st.plotly_chart(fig_corr)
                    st.markdown("""
                    **Interpretation Tip:**  
                    - A cell with a value near +1 (red) means the two columns tend to increase together.  
                    - A cell near -1 (blue) means when one goes up, the other goes down.  
                    - 0 (white) means there’s no strong relationship.
                    """)
                else:
                    st.write("No numeric columns found for correlation analysis under current filters.")

            # 2) Simple Guest Segmentation (K-Means)
            st.subheader("2. Guest Segmentation (K-Means)")
            st.write("""
            We can group guests into clusters based on how similar their behaviors or attributes are.
            Here, we use **TotalRevenue** (how much a guest spent) and **GuestFeedbackScore** (how satisfied they are)
            to group guests into segments. 
            
            You can decide how many groups ("clusters") to form. This is a simple example:
            - **Cluster 0**: Might be guests with lower spend but high satisfaction.
            - **Cluster 1**: Possibly guests with higher spend but moderate satisfaction.
            - etc.

            This helps you understand what types of guests you have.
            """)

            if "TotalRevenue" in filtered_data.columns and "GuestFeedbackScore" in filtered_data.columns:
                features = ["TotalRevenue", "GuestFeedbackScore"]
                df_segment = filtered_data[features].dropna()

                if not df_segment.empty:
                    scaler = StandardScaler()
                    X = scaler.fit_transform(df_segment)

                    k = st.slider("Select Number of Clusters (k)", min_value=2, max_value=10, value=3)
                    kmeans = KMeans(n_clusters=k, random_state=42)
                    kmeans.fit(X)
                    labels = kmeans.labels_
                    df_segment["Cluster"] = labels

                    # Create scatter plot
                    fig_kmeans = px.scatter(
                        df_segment, 
                        x="TotalRevenue", 
                        y="GuestFeedbackScore", 
                        color="Cluster", 
                        title=f"Guest Segmentation (k={k})",
                        color_continuous_scale="Viridis"
                    )
                    st.plotly_chart(fig_kmeans)
                    st.markdown("""
                    **Reading This Chart:**  
                    Each dot is a guest, and the color shows which group (cluster) they belong to.  
                    - Look for clusters with higher revenue but lower feedback (could be guests who pay more but aren’t fully happy).  
                    - Clusters with lower revenue but higher feedback might be guests who love your service but don’t spend much.  

                    You can use this insight to create targeted promotions or improve specific areas of your services.
                    """)
                else:
                    st.write("Not enough data to perform K-Means segmentation (no valid rows).")
            else:
                st.write("Columns 'TotalRevenue' and/or 'GuestFeedbackScore' not found. Cannot perform K-Means segmentation.")

        # ─────────────────────────────────────────────────────────────────────────
        #         NEW SECTIONS ADDED BELOW
        # ─────────────────────────────────────────────────────────────────────────

        # ---------------- CANCELLATION & NO-SHOW ANALYSIS ----------------------
        elif choice == "Cancellation & No-Show Analysis":
            st.header("Cancellation & No-Show Analysis")

            if "ReservationStatus" in filtered_data.columns:
                # Count how many bookings are Completed, Canceled, or No-Show
                status_counts = filtered_data["ReservationStatus"].value_counts().reset_index()
                status_counts.columns = ["ReservationStatus", "Count"]

                fig_status = px.pie(
                    status_counts, 
                    names="ReservationStatus", 
                    values="Count", 
                    title="Reservation Status Breakdown"
                )
                st.plotly_chart(fig_status)

                st.write("**Trend Over Time**")
                # Example: count the number of each status per month
                if "Date" in filtered_data.columns and filtered_data["Date"].notna().any():
                    monthly_status = (
                        filtered_data
                        .groupby([filtered_data["Date"].dt.to_period("M"), "ReservationStatus"])
                        .size()
                        .reset_index(name="Count")
                    )
                    monthly_status["Month"] = monthly_status["Date"].astype(str)

                    fig_status_time = px.line(
                        monthly_status, 
                        x="Month", 
                        y="Count", 
                        color="ReservationStatus",
                        title="Monthly Reservation Status Trend"
                    )
                    st.plotly_chart(fig_status_time)
                else:
                    st.write("No valid Date column to show time trends.")

            else:
                st.write("No 'ReservationStatus' column found. Cannot analyze cancellations or no-shows.")

        # -------------- GUEST RETENTION & REPEAT VISITS ANALYSIS --------------
        elif choice == "Guest Retention & Repeat Visits":
            st.header("Guest Retention & Repeat Visits Analysis")
            st.write("""
            This section helps identify repeat guests vs. first-time guests, 
            and how often guests return over time.
            """)

            if "GuestID" in filtered_data.columns:
                # Count how many times each GuestID appears
                visit_counts = filtered_data.groupby("GuestID").size().reset_index(name="VisitCount")

                # Merge visit counts back to the filtered_data if needed (only if you want further breakdown)
                # For now, let's just show distribution
                st.subheader("Visit Count Distribution")
                fig_visits = px.histogram(
                    visit_counts, 
                    x="VisitCount", 
                    nbins=20, 
                    title="Distribution of Guest Visit Counts"
                )
                st.plotly_chart(fig_visits)

                # Example classification: if VisitCount > 1, repeat guest; else first-time
                visit_counts["GuestType"] = visit_counts["VisitCount"].apply(lambda x: "Repeat" if x > 1 else "First-Time")
                classification_counts = visit_counts["GuestType"].value_counts().reset_index()
                classification_counts.columns = ["GuestType", "Count"]

                fig_class = px.pie(
                    classification_counts, 
                    names="GuestType", 
                    values="Count", 
                    title="First-Time vs. Repeat Guests"
                )
                st.plotly_chart(fig_class)

            else:
                st.write("No 'GuestID' column found. Cannot analyze repeat visits or retention.")

        # --------- MARKETING ROI & CAMPAIGN PERFORMANCE ANALYSIS --------------
        elif choice == "Marketing ROI & Campaign Performance":
            st.header("Marketing ROI & Campaign Performance (Filtered)")

            st.write("""
            Evaluate how effective your marketing spend is at generating revenue, 
            and compare different marketing channels or campaigns.
            """)

            # Basic ROI: TotalRevenue / MarketingSpend
            if "TotalRevenue" in filtered_data.columns and "MarketingSpend" in filtered_data.columns:
                total_marketing_spend = filtered_data["MarketingSpend"].sum()
                total_revenue = filtered_data["TotalRevenue"].sum()

                if total_marketing_spend > 0:
                    roi_value = total_revenue / total_marketing_spend
                    st.metric("Overall ROI (Revenue/MarketingSpend)", f"{roi_value:.2f}")
                else:
                    st.write("No Marketing Spend available (sum is 0).")

                # Breakdown by MarketingChannel if present
                if "MarketingChannel" in filtered_data.columns:
                    channel_df = filtered_data.groupby("MarketingChannel").agg({
                        "MarketingSpend": "sum",
                        "TotalRevenue": "sum"
                    }).reset_index()

                    # Avoid divide by zero
                    channel_df["ROI"] = channel_df.apply(
                        lambda row: row["TotalRevenue"] / row["MarketingSpend"] if row["MarketingSpend"] else 0, 
                        axis=1
                    )

                    fig_channel = px.bar(
                        channel_df, 
                        x="MarketingChannel", 
                        y="ROI",
                        title="ROI by Marketing Channel",
                        hover_data=["MarketingSpend", "TotalRevenue"]
                    )
                    st.plotly_chart(fig_channel)

            else:
                st.write("Missing 'TotalRevenue' or 'MarketingSpend' columns. Cannot calculate marketing ROI.")

        # ---- OPERATIONAL EFFICIENCY & RESOURCE ALLOCATION ANALYSIS -----------
        elif choice == "Operational Efficiency & Resource Allocation":
            st.header("Operational Efficiency & Resource Allocation (Filtered)")
            st.write("""
            Analyze staffing levels, occupancy, maintenance tickets, and other operational metrics to 
            optimize resource allocation.
            """)

            # Example: Compare staffing (HousekeepingStaffCount) vs. OccupiedRooms
            if "HousekeepingStaffCount" in filtered_data.columns and "OccupiedRooms" in filtered_data.columns:
                staff_vs_occupancy = filtered_data.groupby(filtered_data["Date"].dt.to_period("M")).agg({
                    "HousekeepingStaffCount": "mean",
                    "OccupiedRooms": "mean"
                }).reset_index()
                staff_vs_occupancy["Date"] = staff_vs_occupancy["Date"].astype(str)

                fig_staff = px.line(
                    staff_vs_occupancy,
                    x="Date",
                    y=["HousekeepingStaffCount", "OccupiedRooms"],
                    title="Staffing Levels vs. Occupancy (Monthly Average)",
                    markers=True
                )
                st.plotly_chart(fig_staff)
            else:
                st.write("Required columns for staffing vs occupancy not found.")

            # Example placeholder: Maintenance tickets (if you had a MaintenanceTickets column)
            if "MaintenanceTickets" in filtered_data.columns:
                maint_monthly = (
                    filtered_data
                    .groupby(filtered_data["Date"].dt.to_period("M"))["MaintenanceTickets"]
                    .sum()
                    .reset_index()
                )
                maint_monthly["Date"] = maint_monthly["Date"].astype(str)

                fig_maint = px.bar(
                    maint_monthly,
                    x="Date",
                    y="MaintenanceTickets",
                    title="Monthly Maintenance Tickets"
                )
                st.plotly_chart(fig_maint)
            else:
                st.write("No 'MaintenanceTickets' column found to analyze service requests.")

        # ----------------- ROOM Type Profitability Analysis -------------------
        elif choice == "Room Type Profitability Analysis":
            st.header("Room Type Profitability Analysis")
            st.write("""
            Analyze the net revenue, profit margin (if costs are available), and occupancy rates by room type
            to see which room types are most profitable.
            """)

            # Example: Summaries by room type columns if they exist
            # SingleRoomRevenue, DoubleRoomRevenue, RoyalRoomRevenue, FamilyRoomRevenue
            if all(col in filtered_data.columns for col in ["SingleRoomRevenue", "DoubleRoomRevenue", "RoyalRoomRevenue", "FamilyRoomRevenue"]):
                profitability_df = pd.DataFrame({
                    "SingleRoomRevenue": [filtered_data["SingleRoomRevenue"].sum()],
                    "DoubleRoomRevenue": [filtered_data["DoubleRoomRevenue"].sum()],
                    "RoyalRoomRevenue": [filtered_data["RoyalRoomRevenue"].sum()],
                    "FamilyRoomRevenue": [filtered_data["FamilyRoomRevenue"].sum()],  # Add Family Room
                })
                melted = profitability_df.melt(var_name="RoomType", value_name="Revenue")

                fig_room_revenue = px.bar(
                    melted,
                    x="RoomType",
                    y="Revenue",
                    title="Total Revenue by Room Type"
                )
                st.plotly_chart(fig_room_revenue)
            else:
                st.write("No room-type revenue columns found (SingleRoomRevenue, DoubleRoomRevenue, RoyalRoomRevenue, FamilyRoomRevenue).")

            # Occupancy rates per room type (very rough, depends on your data design)
            # If you track SingleRoomsOccupied, DoubleRoomsOccupied, RoyalRoomsOccupied, FamilyRoomsOccupied
            if all(col in filtered_data.columns for col in ["SingleRoomsOccupied", "DoubleRoomsOccupied", "RoyalRoomsOccupied", "FamilyRoomsOccupied", "AvailableRooms"]):
                # Summation approach
                total_single_occupied = filtered_data["SingleRoomsOccupied"].sum()
                total_double_occupied = filtered_data["DoubleRoomsOccupied"].sum()
                total_royal_occupied = filtered_data["RoyalRoomsOccupied"].sum()
                total_family_occupied = filtered_data["FamilyRoomsOccupied"].sum()  # Add Family Room
                total_rooms_available = filtered_data["AvailableRooms"].sum()

                st.subheader("Room Type Occupancy (Aggregated)")
                st.write(f"**Single Rooms Occupied (sum):** {total_single_occupied}")
                st.write(f"**Double Rooms Occupied (sum):** {total_double_occupied}")
                st.write(f"**Royal Rooms Occupied (sum):** {total_royal_occupied}")
                st.write(f"**Family Rooms Occupied (sum):** {total_family_occupied}")  # Add Family Room
                st.write(f"**Total 'AvailableRooms' (sum):** {total_rooms_available}")
            else:
                st.write("Cannot calculate occupancy rates by room type—columns are missing.")

        # --------------------- CLTV (CUSTOMER LIFETIME VALUE) ------------------
        elif choice == "CLTV Estimation":
            st.header("Customer Lifetime Value (CLTV) Estimation")
            st.write("""
            Estimate how valuable each guest is over their entire “lifetime” with your property.
            This can guide marketing and retention strategies.
            """)

            if "GuestID" in filtered_data.columns and "TotalRevenue" in filtered_data.columns:
                # Example approach:
                # 1) Sum revenue by GuestID
                # 2) Count visits by GuestID
                # 3) CLTV = sum revenue per guest (or average revenue per visit * number of visits)
                grouped = filtered_data.groupby("GuestID").agg({
                    "TotalRevenue": "sum"
                }).reset_index()
                grouped.rename(columns={"TotalRevenue": "TotalSpent"}, inplace=True)

                # Simple example: we define CLTV as total spent (not factoring in advanced churn modeling)
                grouped["CLTV"] = grouped["TotalSpent"]  # Placeholder

                st.subheader("Top 10 Guests by CLTV")
                top_10 = grouped.nlargest(10, "CLTV")
                fig_cltv = px.bar(
                    top_10,
                    x="GuestID",
                    y="CLTV",
                    title="Top 10 Guests by Estimated CLTV"
                )
                st.plotly_chart(fig_cltv)
            else:
                st.write("Missing 'GuestID' or 'TotalRevenue' columns for CLTV calculation.")

        # ----------------- UPSELLING & CROSS-SELLING ANALYSIS ------------------
        elif choice == "Upselling & Cross-Selling":
            st.header("Upselling & Cross-Selling Analysis (Filtered)")
            st.write("""
            Review revenue from upsells (like spa, F&B, or room upgrades) and see which items or services 
            are most popular among guests.
            """)

            # Placeholder: Summation of additional revenue columns
            potential_upsell_cols = ["F&B Revenue", "Spa Revenue", "Event Revenue", "RestaurantRevenue", "MerchandiseRevenue"]
            upsell_cols_present = [col for col in potential_upsell_cols if col in filtered_data.columns]

            if upsell_cols_present:
                upsell_sums = filtered_data[upsell_cols_present].sum().reset_index()
                upsell_sums.columns = ["UpsellCategory", "TotalRevenue"]
                fig_upsell = px.pie(
                    upsell_sums, 
                    names="UpsellCategory", 
                    values="TotalRevenue",
                    title="Upsell/Cross-Sell Revenue Breakdown"
                )
                st.plotly_chart(fig_upsell)

                st.write("**Correlation with TotalRevenue**")
                # Check correlation if "TotalRevenue" is present
                if "TotalRevenue" in filtered_data.columns:
                    for col in upsell_cols_present:
                        correlation = filtered_data[[col, "TotalRevenue"]].corr().iloc[0,1]
                        st.write(f"- Correlation between {col} and TotalRevenue: **{correlation:.2f}**")
                else:
                    st.write("No 'TotalRevenue' column to check correlation with upsell items.")
            else:
                st.write("No dedicated upsell/cross-sell columns found (e.g., F&B Revenue, Spa Revenue, etc.).")

        # ------------------------ ROOM COST ANALYSIS ---------------------------
        elif choice == "Room Cost Analysis":
            st.header("Room Cost Analysis")
            st.write("""
            Analyze the cost of rooms, compare it with revenue and profit, and identify the most profitable rooms.
            """)

            # Monthly Cost vs Revenue vs Profit Chart
            st.subheader("Monthly Cost vs Revenue vs Profit")
            if "Date" in filtered_data.columns and "TotalRevenue" in filtered_data.columns and "Profit" in filtered_data.columns:
                monthly_data = (
                    filtered_data
                    .groupby(filtered_data["Date"].dt.to_period("M").astype(str))
                    .agg({
                        "TotalRevenue": "sum",
                        "Profit": "sum",
                        "RoomCost": "sum"
                    })
                    .reset_index()
                )
                monthly_data.rename(columns={"Date": "Month"}, inplace=True)

                fig_monthly = px.line(
                    monthly_data,
                    x="Month",
                    y=["TotalRevenue", "Profit", "RoomCost"],
                    title="Monthly Revenue, Profit, and Room Cost",
                    markers=True
                )
                st.plotly_chart(fig_monthly)
                with st.expander("Explain Monthly Cost vs Revenue vs Profit"):
                    st.markdown("""
                    This chart shows how revenue, profit, and room costs change over time.
                    - **TotalRevenue**: Total revenue generated each month.
                    - **Profit**: Total profit after deducting all costs.
                    - **RoomCost**: Total cost of rooms for each month.
                    """)
                    st.markdown("""
                    **يُظهر هذا الرسم البياني كيفية تغير الإيرادات والأرباح وتكاليف الغرف بمرور الوقت.**
                    - **إجمالي الإيرادات**: إجمالي الإيرادات التي تم تحقيقها كل شهر.
                    - **الربح**: إجمالي الربح بعد خصم جميع التكاليف.
                    - **تكلفة الغرف**: إجمالي تكلفة الغرف لكل شهر.
                    """)
            else:
                st.write("Required columns for monthly cost vs revenue vs profit analysis are missing.")

            # Top 10 Profitable Rooms Chart
            st.subheader("Top 10 Profitable Rooms")
            if "RoomType" in filtered_data.columns and "Profit" in filtered_data.columns:
                room_profit = (
                    filtered_data
                    .groupby("RoomType")["Profit"]
                    .sum()
                    .reset_index()
                    .sort_values("Profit", ascending=False)
                    .head(10)
                )
                fig_top_rooms = px.bar(
                    room_profit,
                    x="RoomType",
                    y="Profit",
                    title="Top 10 Profitable Rooms",
                    labels={"Profit": "Total Profit", "RoomType": "Room Type"}
                )
                st.plotly_chart(fig_top_rooms)
                with st.expander("Explain Top 10 Profitable Rooms"):
                    st.markdown("""
                    This chart shows the top 10 most profitable room types based on total profit.
                    Use this to identify which room types are generating the most profit.
                    """)
                    st.markdown("""
                    **يُظهر هذا الرسم البياني أفضل 10 أنواع غرف من حيث الربح الإجمالي.**
                    **استخدم هذا لتحديد أنواع الغرف التي تحقق أكبر ربح.**
                    """)
            else:
                st.write("Need Adjusting strategy.")

        # ------------------------ DYNAMIC PRICING SUGGESTIONS ------------------
        elif choice == "Dynamic Pricing Suggestions":
            st.header("Dynamic Pricing Suggestions")
            st.write("""
            Optimize room pricing strategies based on historical data, demand, and competition.
            The suggested pricing is calculated using regression analysis on historical data.
            """)

            if "Date" in filtered_data.columns and "ADR" in filtered_data.columns:
                # Prepare the data for regression analysis
                pricing_data = filtered_data[["Date", "ADR", "OccupiedRooms"]].dropna()
                pricing_data["DayOfWeek"] = pricing_data["Date"].dt.dayofweek  # Add day of the week as a feature

                # Train a regression model
                from sklearn.model_selection import train_test_split
                from sklearn.linear_model import LinearRegression

                X = pricing_data[["DayOfWeek", "OccupiedRooms"]]
                y = pricing_data["ADR"]
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                model = LinearRegression()
                model.fit(X_train, y_train)

                # Predict optimal pricing for the next 7 days
                next_week = pd.date_range(start=filtered_data["Date"].max() + timedelta(days=1), periods=7)
                next_week_data = pd.DataFrame({
                    "DayOfWeek": next_week.dayofweek,
                    "OccupiedRooms": [filtered_data["OccupiedRooms"].mean()] * 7
                })
                predictions = model.predict(next_week_data)

                # Display predictions
                st.subheader("Recommended Pricing for the Next 7 Days")
                prediction_df = pd.DataFrame({"Date": next_week, "Recommended ADR": predictions})
                st.table(prediction_df)

        # ------------------------ GUEST PREFERENCES ----------------------------
        elif choice == "Guest Preferences":
            st.header("Guest Preferences Recommendations")
            st.write("""
            Provide personalized recommendations to guests based on their preferences and booking history.
            """)

            if "GuestID" in filtered_data.columns and "LoyaltyTier" in filtered_data.columns:
                # Example: Recommend room upgrades for Platinum loyalty members
                platinum_guests = filtered_data[filtered_data["LoyaltyTier"] == "Platinum"]

                st.subheader("Upgrade Recommendations for Platinum Guests")
                if not platinum_guests.empty:
                    platinum_guests["UpgradeRecommendation"] = "Royal Room"
                    st.write(platinum_guests[["GuestID", "LoyaltyTier", "UpgradeRecommendation"]].head(10))
                else:
                    st.write("No Platinum members in the filtered data.")

        # ------------------------ SCENARIO PLANNING ----------------------------
        elif choice == "Scenario Planning":
            st.header("Scenario Planning")
            st.write("""
            Simulate the impact of different scenarios (e.g., price changes, marketing spend) on revenue and occupancy.
            """)

            # Example: Simulate impact of increasing ADR by 10%
            st.subheader("Simulate Impact of Price Changes")
            price_change = st.slider("Select Price Change (%)", min_value=-50, max_value=50, value=10)
            new_adr = filtered_data["ADR"] * (1 + price_change / 100)

            # Calculate new revenue
            new_revenue = new_adr * filtered_data["OccupiedRooms"]

            # Display results
            st.write(f"With a {price_change}% change in ADR:")
            st.write(f"Estimated Total Revenue: ${new_revenue.sum():,.2f}")

        elif choice == "Story Telling":
            st.header("Detailed Data Story & Insights")

            # Here you can create a narrative summary using key metrics
            # Adjust the text as you like. The code checks for columns before using them.

            # 1) Basic Date Range
            if "Date" in filtered_data.columns and filtered_data["Date"].notna().any():
                min_date = filtered_data["Date"].min().date()
                max_date = filtered_data["Date"].max().date()
                st.markdown(f"- **Data Range:** {min_date} to {max_date}")
            else:
                st.markdown("- **Data Range:** Not available (missing or invalid Date column).")

            # 2) Basic Row Count
            total_rows = len(filtered_data)
            st.markdown(f"- **Number of Records (after filters):** {total_rows}")

            # 3) Overall Revenue & Profit
            if "TotalRevenue" in filtered_data.columns:
                total_revenue = filtered_data["TotalRevenue"].sum()
                st.markdown(f"- **Total Revenue (Filtered):** ${total_revenue:,.2f}")
            else:
                st.markdown("- **Total Revenue:** Not available in dataset.")

            if "Profit" in filtered_data.columns:
                total_profit = filtered_data["Profit"].sum()
                st.markdown(f"- **Total Profit (Filtered):** ${total_profit:,.2f}")
            else:
                st.markdown("- **Total Profit:** Not available in dataset.")

            # 4) Occupancy & ADR
            occupancy_rate = None
            if all(col in filtered_data.columns for col in ["OccupiedRooms", "AvailableRooms"]):
                if filtered_data["AvailableRooms"].sum() > 0:
                    occupancy_rate = (
                        filtered_data["OccupiedRooms"].sum()
                        / filtered_data["AvailableRooms"].sum()
                        * 100
                    )
                    st.markdown(f"- **Overall Occupancy Rate:** {occupancy_rate:.2f}%")
                else:
                    st.markdown("- **Occupancy Rate:** AvailableRooms sum is zero, cannot compute.")
            else:
                st.markdown("- **Occupancy Rate:** Missing OccupiedRooms/AvailableRooms columns.")

            if "ADR" in filtered_data.columns:
                avg_adr = filtered_data["ADR"].mean()
                st.markdown(f"- **Average ADR:** ${avg_adr:,.2f}")
            else:
                st.markdown("- **Average ADR:** Missing ADR column.")

            # 5) Identify Potential Weak Points or Observations
            st.subheader("Potential Weak Points & Observations")
            # Example checks:
            # a) If Occupancy is low
            if occupancy_rate is not None and occupancy_rate < 40:
                st.markdown("- **Low Occupancy:** Occupancy is below 40%. Consider targeted marketing or promotions.")
            # b) If Profit is negative
            if "Profit" in filtered_data.columns and total_profit < 0:
                st.markdown("- **Negative Profit:** Overall profit is negative. Review costs or increase revenue strategies.")
            # c) If feedback is present but below a threshold
            if "GuestFeedbackScore" in filtered_data.columns:
                avg_feedback = filtered_data["GuestFeedbackScore"].mean()
                if avg_feedback < 6:
                    st.markdown("- **Low Guest Satisfaction:** Average feedback score is below 6/10. Investigate common complaints.")
            
            # d) If marketing ROI is suspiciously low
            if all(col in filtered_data.columns for col in ["MarketingSpend", "TotalRevenue"]):
                total_marketing_spend = filtered_data["MarketingSpend"].sum()
                if total_marketing_spend > 0:
                    marketing_roi = total_revenue / total_marketing_spend
                    if marketing_roi < 1:
                        st.markdown("- **Low Marketing ROI:** Revenue < MarketingSpend. Refine campaigns or reduce spend.")
            
            # 6) Simple Narrative Explanation
            st.write("----")
            st.markdown("## Narrative Summary")
            st.write(
                """
                Based on the filtered dataset:
                - We analyzed the time period to understand how revenue, occupancy, and satisfaction scores evolve.
                - The data indicates certain areas (like low occupancy or negative profit) that require attention.
                - **Recommendations** might include adjusting room rates (if ADR is too low or too high), 
                  refining marketing strategies to improve ROI, or focusing on guest experience for better feedback scores.

                Overall, these insights guide you to **focus on improving weak spots** such as 
                guest satisfaction, marketing optimization, or cost reduction in housekeeping and maintenance. 
                """
            )
            
            # You can also add expansions in other languages (e.g. Arabic).
            # Example short Arabic summary:
            st.markdown("### ملخص باللغة العربية")
            st.write(
                """
                من خلال تحليل البيانات الحالية:
                - قمنا بدراسة الفترة الزمنية من حيث الإيرادات، الإشغال، وتقييمات الضيوف.
                - تشير النتائج إلى بعض النقاط الضعيفة مثل انخفاض معدل الإشغال أو الربح السلبي.
                - التوصيات قد تتضمن تعديل أسعار الغرف أو تحسين استراتيجية التسويق وتحسين تجربة الضيوف.

                بشكل عام، يمكن استخدام هذه النتائج لتوجيه الجهود نحو تحسين المجالات الأضعف مثل
                رضا الضيوف وتحسين فعالية الإنفاق التسويقي أو تقليل التكاليف الزائدة.
                """
            )

        # ------------------------ DIG DEEPER -----------------------------------
        elif choice == "Dig Deeper":
            st.header("Dig Deeper Analysis")
            st.write("""
            Compare exactly two columns and analyze their relationship with multiple chart options.
            """)

            # Get all columns
            all_columns = filtered_data.columns.tolist()
            
            # Force user to select exactly 2 columns
            selected_columns = st.multiselect(
                "Select exactly two columns to compare", 
                options=all_columns, 
                default=all_columns[:2]
            )

            # Check the number of selected columns
            if len(selected_columns) < 2:
                st.warning("Please select 2 columns to proceed.")
            elif len(selected_columns) > 2:
                st.warning("Please select only 2 columns to proceed.")
            else:
                # Extract the two columns
                col1, col2 = selected_columns
                st.subheader(f"Comparison: **{col1}** vs **{col2}**")

                # Determine if columns are numeric or categorical
                col1_is_numeric = pd.api.types.is_numeric_dtype(filtered_data[col1])
                col2_is_numeric = pd.api.types.is_numeric_dtype(filtered_data[col2])

                # ---------------------------------------------------------
                # CASE 1: Both columns are numeric
                # ---------------------------------------------------------
                if col1_is_numeric and col2_is_numeric:
                    st.markdown("**Both variables are numeric.** Below are the best ways to visualize their relationship:")

                    # Scatter Plot
                    scatter_fig = px.scatter(
                        filtered_data,
                        x=col1,
                        y=col2,
                        title=f"Scatter Plot: {col1} vs {col2}"
                    )
                    st.plotly_chart(scatter_fig)

                    # Line Chart
                    line_fig = px.line(
                        filtered_data,
                        x=col1,
                        y=col2,
                        title=f"Line Chart: {col1} vs {col2}"
                    )
                    st.plotly_chart(line_fig)

                    # Correlation Heatmap
                    corr = filtered_data[[col1, col2]].corr().iloc[0, 1]
                    heatmap_fig = px.imshow(
                        filtered_data[[col1, col2]].corr(),
                        text_auto=True,
                        color_continuous_scale='RdBu_r',
                        title=f"Correlation Heatmap: {col1} vs {col2}"
                    )
                    st.plotly_chart(heatmap_fig)

                    # Explanation
                    with st.expander("View Explanation"):
                        st.write(f"**Correlation between {col1} and {col2}:** {corr:.2f}")
                        if corr > 0.7:
                            st.write("There is a **strong positive correlation** between the two variables. As one increases, the other tends to increase as well.")
                        elif corr < -0.7:
                            st.write("There is a **strong negative correlation** between the two variables. As one increases, the other tends to decrease.")
                        else:
                            st.write("The correlation is **weak or moderate**. There is no strong linear relationship between the two variables.")

                # ---------------------------------------------------------
                # CASE 2: One numeric, one categorical
                # ---------------------------------------------------------
                elif (col1_is_numeric and not col2_is_numeric) or (not col1_is_numeric and col2_is_numeric):
                    st.markdown("**One variable is numeric and the other is categorical.** Below are the best ways to visualize their relationship:")

                    # Identify which is categorical and which is numeric
                    if col1_is_numeric:
                        numeric_col = col1
                        cat_col = col2
                    else:
                        numeric_col = col2
                        cat_col = col1

                    # Bar Chart
                    cat_bar_fig = px.bar(
                        filtered_data,
                        x=cat_col,
                        y=numeric_col,
                        title=f"Bar Chart: {cat_col} vs {numeric_col}"
                    )
                    st.plotly_chart(cat_bar_fig)

                    # Box Plot
                    box_fig = px.box(
                        filtered_data,
                        x=cat_col,
                        y=numeric_col,
                        title=f"Box Plot: {cat_col} vs {numeric_col}"
                    )
                    st.plotly_chart(box_fig)

                    # Violin Plot
                    violin_fig = px.violin(
                        filtered_data,
                        x=cat_col,
                        y=numeric_col,
                        box=True,
                        points="all",
                        title=f"Violin Plot: {cat_col} vs {numeric_col}"
                    )
                    st.plotly_chart(violin_fig)

                    # Explanation
                    with st.expander("View Explanation"):
                        mean_by_cat = filtered_data.groupby(cat_col)[numeric_col].mean().reset_index(name="mean_value")
                        highest_cat = mean_by_cat.loc[mean_by_cat["mean_value"].idxmax(), cat_col]
                        highest_mean = mean_by_cat["mean_value"].max()

                        st.write(f"The category **{highest_cat}** has the highest average value of **{numeric_col}** ({highest_mean:.2f}).")
                        st.write("The **Box Plot** and **Violin Plot** show the distribution of the numeric variable across categories, including potential outliers.")

                # ---------------------------------------------------------
                # CASE 3: Both columns are categorical
                # ---------------------------------------------------------
                else:
                    st.markdown("**Both variables are categorical.** Below are the best ways to visualize their relationship:")

                    # Grouped Bar Chart
                    grouped_data = filtered_data.groupby([col1, col2]).size().reset_index(name='count')
                    grouped_bar_fig = px.bar(
                        grouped_data,
                        x=col1,
                        y='count',
                        color=col2,
                        barmode='group',
                        title=f"Grouped Bar Chart: {col1} vs {col2}"
                    )
                    st.plotly_chart(grouped_bar_fig)

                    # Sunburst Chart
                    sunburst_fig = px.sunburst(
                        grouped_data,
                        path=[col1, col2],
                        values='count',
                        title=f"Sunburst Chart: {col1} vs {col2}"
                    )
                    st.plotly_chart(sunburst_fig)

                    # Heatmap
                    heatmap_fig = px.density_heatmap(
                        filtered_data,
                        x=col1,
                        y=col2,
                        title=f"Heatmap: {col1} vs {col2}"
                    )
                    st.plotly_chart(heatmap_fig)

                    # Explanation
                    with st.expander("View Explanation"):
                        max_count = grouped_data['count'].max()
                        most_frequent = grouped_data[grouped_data['count'] == max_count]

                        if len(most_frequent) == 1:
                            top_c1 = most_frequent[col1].values[0]
                            top_c2 = most_frequent[col2].values[0]
                            st.write(f"The most frequent combination is: **{col1} = {top_c1}** and **{col2} = {top_c2}**, with a count of **{max_count}**.")
                        else:
                            st.write(f"There are multiple combinations with the highest frequency, each having a count of **{max_count}**.")
      # ─────────────────────────────────────────────────────────────────────────

        # (NEW) COMPANY'S ANALYSIS
        # ─────────────────────────────────────────────────────────────────────────
        elif choice == "Company's":
            st.header("Company Analysis")

            # Ensure the necessary columns exist
            if "Company" not in filtered_data.columns or "CompanyDiscount" not in filtered_data.columns:
                st.warning("Company' and 'CompanyDiscount'")
            else:
                # 1) YEAR & QUARTER CALCULATION
                # If not already created above:
                if "Quarter" not in filtered_data.columns:
                    if "Date" in filtered_data.columns and filtered_data["Date"].notna().any():
                        filtered_data["Quarter"] = filtered_data["Date"].dt.quarter
                    else:
                        filtered_data["Quarter"] = 0  # fallback if date is missing or invalid

                # 2) TOTAL REVENUE FROM EACH COMPANY BY YEAR & QUARTER
                st.subheader("Total Revenue by Company, Year, and Quarter")
                if "TotalRevenue" in filtered_data.columns:
                    revenue_by_company = (
                        filtered_data.groupby(["Company", "Year", "Quarter"])["TotalRevenue"]
                        .sum()
                        .reset_index()
                    )

                    if not revenue_by_company.empty:
                        fig_revenue_company = px.bar(
                            revenue_by_company,
                            x="Year",
                            y="TotalRevenue",
                            color="Quarter",
                            facet_col="Company",
                            facet_col_wrap=3,  # one chart per Company
                            title="Company Revenue by Year & Quarter (Filtered)",
                            barmode="group"
                        )
                        fig_revenue_company.for_each_annotation(
    lambda a: a.update(text=a.text.split("=")[-1])
)

                        st.plotly_chart(fig_revenue_company)

                        with st.expander("Explanation (English & Arabic)"):
                            st.markdown("### English Explanation")
                            st.write("""
                            - **Chart**: Each Company's revenue is broken down by Year on the X-axis and colored by Quarter.
                            - **Interpretation**: You can see how each Company’s revenue changes across different years and quarters. 
                              Look for quarters with higher bars to identify peak periods of spending or partnership performance.
                            """)
                           
                    else:
                        st.write("No revenue data (TotalRevenue) available under current filters.")
                else:
                    st.write("No 'TotalRevenue' column found. Cannot analyze company revenue.")

                # 3) COMPANY DISCOUNT USAGE (FREQUENCY & AMOUNT) BY YEAR
                st.subheader("Company Discount Usage by Year")
                # We assume CompanyDiscount is numeric (e.g., discount amount).
                # If it's a boolean or code, adjust accordingly.
                discount_usage = (
                    filtered_data.groupby(["Company", "Year"])["CompanyDiscount"]
                    .agg(["count", "sum"])
                    .reset_index()
                )
                discount_usage.rename(columns={"count": "UsageCount", "sum": "DiscountSum"}, inplace=True)

                if not discount_usage.empty:
                    # A bar chart for usage count
                    fig_discount_count = px.bar(
                        discount_usage,
                        x="Year",
                        y="UsageCount",
                        color="Company",
                        barmode="group",
                        title="Company Discount - Frequency of Usage by Year"
                    )
                    st.plotly_chart(fig_discount_count)

                    # Another bar chart for total discount sum
                    fig_discount_sum = px.bar(
                        discount_usage,
                        x="Year",
                        y="DiscountSum",
                        color="Company",
                        barmode="group",
                        title="Company Discount - Total Discount Amount by Year"
                    )
                    st.plotly_chart(fig_discount_sum)

                    with st.expander("Explanation (English & Arabic)"):
                        st.markdown("### English Explanation")
                        st.write("""
                        - **Frequency of Usage**: Shows how many times the discount was applied (UsageCount).
                        - **Total Discount Amount**: Shows the sum of all discount values used in each year (DiscountSum).
                        - High usage may indicate a popular or beneficial discount for that company, 
                          while a high total sum shows the overall monetary impact.
                        """)
                        st.markdown("---")
                       
                else:
                    st.write("No discount usage data found under the current filters.")

        # (Keep the rest of your code sections unchanged below ...)
        
        # ------------------------ SIDEBAR FOOTER -------------------------------
    