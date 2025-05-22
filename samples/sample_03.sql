-- 복잡한 MyBatis 동적 쿼리 샘플
-- 파일명: complex_mybatis_query.sql
-- 설명: 고급 보고서 생성을 위한 복잡한 동적 쿼리

<select id="generateSalesReport" resultMap="SalesReportMap">
    WITH monthly_sales AS (
        SELECT 
            TO_CHAR(s.sale_date, 'YYYY-MM') as sale_month,
            p.product_category,
            <choose>
                <when test="groupByRegion">
                    c.region,
                </when>
                <when test="groupByStore">
                    s.store_id,
                </when>
                <otherwise>
                    'ALL' as region,
                </otherwise>
            </choose>
            SUM(s.quantity) as total_quantity,
            SUM(s.quantity * s.unit_price) as total_amount,
            COUNT(DISTINCT s.customer_id) as customer_count
        FROM 
            sales s
        JOIN 
            products p ON s.product_id = p.product_id
        JOIN 
            customers c ON s.customer_id = c.customer_id
        <where>
            <if test="startDate != null">
                s.sale_date >= TO_DATE(#{startDate}, 'YYYY-MM-DD')
            </if>
            <if test="endDate != null">
                AND s.sale_date &lt;= TO_DATE(#{endDate}, 'YYYY-MM-DD')
            </if>
            <if test="productCategories != null and productCategories.size() > 0">
                AND p.product_category IN
                <foreach item="category" collection="productCategories" open="(" separator="," close=")">
                    #{category}
                </foreach>
            </if>
            <if test="regions != null and regions.size() > 0">
                AND c.region IN
                <foreach item="region" collection="regions" open="(" separator="," close=")">
                    #{region}
                </foreach>
            </if>
            <if test="storeIds != null and storeIds.size() > 0">
                AND s.store_id IN
                <foreach item="storeId" collection="storeIds" open="(" separator="," close=")">
                    #{storeId}
                </foreach>
            </if>
            <if test="minPurchaseAmount != null">
                AND s.quantity * s.unit_price >= #{minPurchaseAmount}
            </if>
            <if test="customerSegment != null">
                AND c.customer_segment = #{customerSegment}
            </if>
        </where>
        GROUP BY 
            TO_CHAR(s.sale_date, 'YYYY-MM'),
            p.product_category,
            <choose>
                <when test="groupByRegion">
                    c.region
                </when>
                <when test="groupByStore">
                    s.store_id
                </when>
                <otherwise>
                    'ALL'
                </otherwise>
            </choose>
    ),
    previous_period AS (
        SELECT 
            <choose>
                <when test="compareWithPreviousYear">
                    TO_CHAR(ADD_MONTHS(TO_DATE(sale_month, 'YYYY-MM'), 12), 'YYYY-MM') as current_month,
                </when>
                <otherwise>
                    TO_CHAR(ADD_MONTHS(TO_DATE(sale_month, 'YYYY-MM'), 1), 'YYYY-MM') as current_month,
                </otherwise>
            </choose>
            product_category,
            <choose>
                <when test="groupByRegion">
                    region,
                </when>
                <when test="groupByStore">
                    store_id,
                </when>
                <otherwise>
                    'ALL' as region,
                </otherwise>
            </choose>
            total_quantity as prev_quantity,
            total_amount as prev_amount,
            customer_count as prev_customer_count
        FROM 
            monthly_sales
    )
    SELECT 
        ms.sale_month,
        ms.product_category,
        <choose>
            <when test="groupByRegion">
                ms.region as group_by_field,
                r.region_name as group_by_name,
            </when>
            <when test="groupByStore">
                ms.store_id as group_by_field,
                s.store_name as group_by_name,
            </when>
            <otherwise>
                'ALL' as group_by_field,
                'All Regions' as group_by_name,
            </otherwise>
        </choose>
        ms.total_quantity,
        ms.total_amount,
        ms.customer_count,
        pp.prev_quantity,
        pp.prev_amount,
        pp.prev_customer_count,
        CASE 
            WHEN pp.prev_amount IS NULL OR pp.prev_amount = 0 THEN NULL
            ELSE ROUND((ms.total_amount - pp.prev_amount) / pp.prev_amount * 100, 2)
        END as amount_growth_percent,
        CASE 
            WHEN pp.prev_quantity IS NULL OR pp.prev_quantity = 0 THEN NULL
            ELSE ROUND((ms.total_quantity - pp.prev_quantity) / pp.prev_quantity * 100, 2)
        END as quantity_growth_percent,
        <if test="includeAvgTicket">
            CASE 
                WHEN ms.customer_count = 0 THEN 0
                ELSE ROUND(ms.total_amount / ms.customer_count, 2)
            END as avg_ticket,
        </if>
        <if test="includeProductDetails">
            (
                SELECT LISTAGG(p.product_name, ', ') WITHIN GROUP (ORDER BY SUM(s.quantity * s.unit_price) DESC)
                FROM sales s
                JOIN products p ON s.product_id = p.product_id
                WHERE TO_CHAR(s.sale_date, 'YYYY-MM') = ms.sale_month
                AND p.product_category = ms.product_category
                <choose>
                    <when test="groupByRegion">
                        AND c.region = ms.region
                    </when>
                    <when test="groupByStore">
                        AND s.store_id = ms.store_id
                    </when>
                </choose>
                GROUP BY p.product_id
                ORDER BY SUM(s.quantity * s.unit_price) DESC
                FETCH FIRST 5 ROWS ONLY
            ) as top_products,
        </if>
        <if test="calculateMarketShare">
            ROUND(ms.total_amount / (
                SELECT SUM(total_amount) 
                FROM monthly_sales 
                WHERE sale_month = ms.sale_month
            ) * 100, 2) as market_share_percent,
        </if>
        <foreach item="metric" collection="customMetrics" separator="," open="" close="">
            <if test="metric == 'CUSTOMER_RETENTION'">
                (
                    SELECT COUNT(DISTINCT s2.customer_id) 
                    FROM sales s1
                    JOIN sales s2 ON s1.customer_id = s2.customer_id
                    WHERE TO_CHAR(s1.sale_date, 'YYYY-MM') = ms.sale_month
                    AND TO_CHAR(s2.sale_date, 'YYYY-MM') = TO_CHAR(ADD_MONTHS(TO_DATE(ms.sale_month, 'YYYY-MM'), -1), 'YYYY-MM')
                    <choose>
                        <when test="groupByRegion">
                            AND s1.region = ms.region
                        </when>
                        <when test="groupByStore">
                            AND s1.store_id = ms.store_id
                        </when>
                    </choose>
                ) as returning_customers,
            </if>
            <if test="metric == 'AVG_ITEMS_PER_SALE'">
                ROUND(ms.total_quantity / COUNT(s.sale_id), 2) as avg_items_per_sale,
            </if>
        </foreach>
        <if test="includeRank">
            RANK() OVER (
                PARTITION BY ms.sale_month 
                ORDER BY 
                <choose>
                    <when test="rankBy == 'AMOUNT'">ms.total_amount</when>
                    <when test="rankBy == 'QUANTITY'">ms.total_quantity</when>
                    <when test="rankBy == 'CUSTOMERS'">ms.customer_count</when>
                    <otherwise>ms.total_amount</otherwise>
                </choose> DESC
            ) as rank_in_period,
        </if>
        <if test="includeTrend">
            CASE
                WHEN pp.prev_amount IS NULL THEN 'NEW'
                WHEN ms.total_amount > pp.prev_amount * 1.1 THEN 'GROWING'
                WHEN ms.total_amount < pp.prev_amount * 0.9 THEN 'DECLINING'
                ELSE 'STABLE'
            END as trend
        </if>
    FROM 
        monthly_sales ms
    LEFT JOIN 
        previous_period pp ON ms.sale_month = pp.current_month 
        AND ms.product_category = pp.product_category
        <choose>
            <when test="groupByRegion">
                AND ms.region = pp.region
            </when>
            <when test="groupByStore">
                AND ms.store_id = pp.store_id
            </when>
            <otherwise>
                AND pp.region = 'ALL'
            </otherwise>
        </choose>
    <choose>
        <when test="groupByRegion">
            LEFT JOIN regions r ON ms.region = r.region_id
        </when>
        <when test="groupByStore">
            LEFT JOIN stores s ON ms.store_id = s.store_id
        </when>
    </choose>
    <where>
        <if test="minSalesAmount != null">
            ms.total_amount >= #{minSalesAmount}
        </if>
        <if test="minCustomerCount != null">
            AND ms.customer_count >= #{minCustomerCount}
        </if>
        <if test="excludeOutliers">
            AND ms.total_amount BETWEEN 
                (SELECT PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY total_amount) FROM monthly_sales)
                AND
                (SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY total_amount) FROM monthly_sales)
        </if>
    </where>
    ORDER BY 
    <choose>
        <when test="orderBy == 'DATE'">
            ms.sale_month
            <if test="orderDirection == 'DESC'">DESC</if>
            <if test="orderDirection != 'DESC'">ASC</if>
        </when>
        <when test="orderBy == 'AMOUNT'">
            ms.total_amount
            <if test="orderDirection == 'DESC'">DESC</if>
            <if test="orderDirection != 'DESC'">ASC</if>
        </when>
        <when test="orderBy == 'GROWTH'">
            amount_growth_percent
            <if test="orderDirection == 'DESC'">DESC</if>
            <if test="orderDirection != 'DESC'">ASC</if>
        </when>
        <otherwise>
            ms.sale_month ASC,
            <choose>
                <when test="groupByRegion">ms.region</when>
                <when test="groupByStore">ms.store_id</when>
                <otherwise>ms.product_category</otherwise>
            </choose>
        </otherwise>
    </choose>
    <if test="limit != null">
        FETCH FIRST #{limit} ROWS ONLY
    </if>
</select>
