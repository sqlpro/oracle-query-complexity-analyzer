-- MyBatis 동적 쿼리 샘플 (XML 형식)
-- 파일명: sample_01.sql
-- 설명: 고객 주문 검색을 위한 동적 쿼리 예시

<select id="findOrdersByCustomerCriteria" resultMap="OrderResultMap">
    SELECT 
        o.order_id, 
        o.order_date, 
        o.total_amount,
        o.status,
        c.customer_id,
        c.customer_name,
        c.email,
        p.payment_method,
        p.payment_status
    FROM 
        orders o
    JOIN 
        customers c ON o.customer_id = c.customer_id
    LEFT JOIN 
        payments p ON o.order_id = p.order_id
    <where>
        <!-- 고객 ID 기준 필터링 -->
        <if test="customerId != null">
            c.customer_id = #{customerId}
        </if>
        
        <!-- 고객 이름 검색 (부분 일치) -->
        <if test="customerName != null and customerName != ''">
            AND UPPER(c.customer_name) LIKE UPPER(CONCAT('%', #{customerName}, '%'))
        </if>
        
        <!-- 주문 날짜 범위 필터링 -->
        <if test="startDate != null">
            AND o.order_date >= TO_DATE(#{startDate}, 'YYYY-MM-DD')
        </if>
        <if test="endDate != null">
            AND o.order_date &lt;= TO_DATE(#{endDate}, 'YYYY-MM-DD')
        </if>
        
        <!-- 주문 금액 범위 필터링 -->
        <if test="minAmount != null">
            AND o.total_amount >= #{minAmount}
        </if>
        <if test="maxAmount != null">
            AND o.total_amount &lt;= #{maxAmount}
        </if>
        
        <!-- 주문 상태 필터링 (다중 선택 가능) -->
        <if test="orderStatuses != null and orderStatuses.size() > 0">
            AND o.status IN
            <foreach item="status" collection="orderStatuses" open="(" separator="," close=")">
                #{status}
            </foreach>
        </if>
        
        <!-- 결제 방법 필터링 -->
        <if test="paymentMethod != null">
            AND p.payment_method = #{paymentMethod}
        </if>
        
        <!-- 결제 상태 필터링 -->
        <choose>
            <when test="paidOnly == true">
                AND p.payment_status = 'PAID'
            </when>
            <when test="unpaidOnly == true">
                AND p.payment_status = 'UNPAID'
            </when>
            <otherwise>
                <!-- 모든 결제 상태 포함 -->
            </otherwise>
        </choose>
    </where>
    
    <!-- 정렬 옵션 -->
    <choose>
        <when test="sortBy == 'date'">
            ORDER BY o.order_date 
            <if test="sortDirection == 'DESC'">DESC</if>
            <if test="sortDirection != 'DESC'">ASC</if>
        </when>
        <when test="sortBy == 'amount'">
            ORDER BY o.total_amount 
            <if test="sortDirection == 'DESC'">DESC</if>
            <if test="sortDirection != 'DESC'">ASC</if>
        </when>
        <when test="sortBy == 'customer'">
            ORDER BY c.customer_name 
            <if test="sortDirection == 'DESC'">DESC</if>
            <if test="sortDirection != 'DESC'">ASC</if>
        </when>
        <otherwise>
            ORDER BY o.order_id DESC
        </otherwise>
    </choose>
    
    <!-- 페이지네이션 -->
    <if test="pageSize != null and pageNum != null">
        OFFSET (#{pageNum} - 1) * #{pageSize} ROWS
        FETCH NEXT #{pageSize} ROWS ONLY
    </if>
</select>
