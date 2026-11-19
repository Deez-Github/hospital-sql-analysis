/*
================================================================================
 TWDP_orders_practice.sql
 Companion drill file - SELECT / WHERE / ORDER BY / CASE / JOIN practice
--------------------------------------------------------------------------------
 This is the supporting practice workbook that sits behind the assignment:
 a wider set of filtering, string, date, CASE and JOIN exercises run against
 the TWDP (Orders / Customers / Products) sample database in SSMS.

 It is kept in the repository as evidence of practice breadth and is NOT
 required to reproduce the hospital analysis. Queries are preserved as written
 during practice, grouped by theme below.

 Themes covered
   - Filtering: =, AND/OR, BETWEEN, IN, NOT IN, LIKE, NOT LIKE
   - Sorting and paging: ORDER BY ASC/DESC, TOP n
   - Aggregation: COUNT, AVG, SUM, GROUP BY, HAVING
   - Strings and dates: UPPER, CONCAT, LEFT/RIGHT/CHARINDEX, YEAR/MONTH,
     DATENAME, DATEPART, EOMONTH, date-range filtering
   - CASE: bucketisation (order size, region, half-year, priority flags)
   - Joins: INNER, LEFT, FULL, multi-table joins, revenue aggregation
================================================================================
*/

use TWDP;
SELECT *
FROM Orders_table

SELECT *
FROM Orders_table
WHERE Product = 'Phone'

select *
from orders_table
where quantity>=4

select *
from orders_table
where Country = 'Canada'

select * 
from orders_table
where quantity between 2 and 4

select * 
from orders_table
where Product = 'Laptop' and Country = 'Nigeria'

select *
from orders_table
where Product in ('Smartwatch' , 'Tablet') and Quantity >= 3

select *
from orders_table
where (product = 'Smartwatch' or product = 'Tablet') and Quantity >=3

select *
from orders_table
where Country in ( 'Nigeria' , 'Ghana' , 'UAE')

select *
from orders_table
where Product not in ('Laptop' , 'Phone')


SELECT *
FROM Orders_table
WHERE Product IN ('Laptop','Tablet') AND Quantity > 2 AND CustomerName NOT LIKE 'J%'

SELECT CustomerName , Country , Quantity
FROM Orders_table
WHERE Quantity between 2 And 4



SELECT top 2 *
FROM Orders_table
ORDER BY OrderDate desc


--Find the three order with highest quantity, displaying then from highest to lowest
SELECT top 3 *
FROM Orders_table
ORDER BY Quantity DESC

--Find the three order with highest quantity, displaying then from lowest to highest
SELECT top 3 *
FROM Orders_table
ORDER BY Quantity ASC

--list all unique country represented in the dataset

SELECT DISTINCT Country
FROM Orders_table

--Count the total number of orders
-- AS is use for a reference name
SELECT COUNT  (*) AS Total_Orders
FROM Orders_table


--
SELECT AVG (Quantity) as Average_Orders
FROM Orders_table


--count the number of order for each product but only include product order 3 times
SELECT Product, Count(*) as order_count
FROM Orders_table
group by product
HAVING  COUNT(*) > 3

-- Display all order from the most recent to the oldest
SELECT *
FROM Orders_table
ORDER BY OrderDate Desc


-- Display all orders sorted by country (A-Z), then by quanity from highest to lowest within each country
SELECT *
FROM Orders_table
ORDER BY Country ASC, Quantity DESC

-- List all unique country and product combination

SELECT DISTINCT Country, Product
FROM Orders_table

-- select the 5 orders with the highest quantity
SELECT TOP  5 *
FROM Orders_table  
ORDER BY Quantity DESC

--Show the 3 most recent orders placed by customers in Nigeria

SELECT TOP  3 *
FROM Orders_table  
WHERE Country = 'Nigeria'
ORDER BY OrderDate DESC

SELECT UPPER(CustomerName)
FROM Orders_table 


SELECT CONCAT (CustomerName,' ',CustomerName)
FROM Orders_table 

SELECT
    LEFT(CustomerName, CHARINDEX(' ', CustomerName) - 1) AS FirstName,
    RIGHT(CustomerName, LEN(CustomerName) - CHARINDEX(' ',CustomerName)) AS LastName
FROM Orders_table;

SELECT YEAR (OrderDate) AS Order_Year
FROM Orders_table 
-- display the order data and their corresponding month numnber
SELECT Month (OrderDate) AS Order_Month, OrderDate
FROM Orders_table 

SELECT DATENAME(MONTH,OrderDate) AS Order_Year,Month (OrderDate) AS Order_Month, Year(OrderDate) AS Order_Year
FROM Orders_table 

SELECT DATEPART(QUARTER,OrderDate) AS Quarter_year,
            OrderDate,
            Year(OrderDate) AS Order_Year
FROM Orders_table


SELECT EOMONTH(OrderDate, -1)
FROM Orders_table;

SELECT *
FROM Orders_table
WHERE OrderDate >= '2026-09-01'
  AND OrderDate < '2026-10-01';


--SELECT DATEDIFF(DAY, OrderDate, DeliveryDate) AS DeliveryDays
--FROM Orders_table;




SELECT
    *,
    CASE
        WHEN Quantity BETWEEN 1 AND 2 THEN 'Small'
        WHEN Quantity BETWEEN 3 AND 4 THEN 'Medium'
        WHEN Quantity >= 5 THEN 'Bulk'
    END AS OrderSize
FROM Orders_table;


SELECT
    *,
    CASE
        WHEN Quantity <=  2 THEN 'Small'
        WHEN Quantity <= 4  THEN 'Medium'
        ELSE 'Bulk'
    END AS OrderSize
FROM Orders_table;

SELECT *,
    CASE 
        WHEN  month (OrderDate) BETWEEN 1 AND 6 THEN 'H1'
        ELSE 'H2'
    END AS Half
From Orders_table


SELECT *,
    CASE
        WHEN Country IN ('Nigeria','Ghana') THEN 'Africa'
        WHEN Country IN ('USA','Canada','Mexico') THEN 'North America'
        ELSE 'Others'
    END AS Region
FROM Orders_table


SELECT *,
    CASE
        WHEN Country = 'Nigeria' THEN 'Africa'
        WHEN Country = 'Ghana' THEN 'Africa'
        WHEN Country = 'USA' THEN 'North America'
        WHEN Country = 'Canada' THEN 'North America'
        WHEN Country =  'Mexico' THEN 'North America'
        ELSE 'Others'
    END AS Region
FROM Orders_table



SELECT *,
    CASE
        WHEN Quantity >= 4  THEN 'High'
        WHEN Product = 'Laptop' and Quantity > 1 THEN 'High'
        ELSE 'Normal'
    END AS PriorityFlag
FROM Orders_table

SELECT SUM(Quantity)As total_qty, Country
FROM Orders_table
WHERE Country IN ('Nigeria','USA', 'Uk')
GROUP BY Country
HAVING SUM(Quantity) >8
ORDER BY total_qty DESC




SELECT TOP 3
    UPPER(CustomerName) AS CustomerName,
    Product,
    MONTH(OrderDate) AS OrderMonth,
    OrderDate
FROM Orders_table
WHERE Product IN ('Laptop', 'Tablet')
ORDER BY OrderDate DESC;



SELECT
    CASE
        WHEN Quantity <= 2 THEN 'Small'
        WHEN Quantity <= 4 THEN 'Medium'
        ELSE 'Bulk'
    END AS OrderSize,
    COUNT(*) AS OrderCount
FROM Orders_table
GROUP BY
    CASE
        WHEN Quantity <= 2 THEN 'Small'
        WHEN Quantity <= 4 THEN 'Medium'
        ELSE 'Bulk'
    END;



SELECT *
FROM Orders AS Ot
INNER JOIN Customers AS C
    ON Ot.CustomerID = C.CustomerID

use TWDP;
SELECT *
FROM Orders

SELECT *
FROM Products

SELECT *
FROM Customers


SELECT 
    O.OrderID,
    C.CustomerName,
    O.OrderDate
FROM Orders AS O
INNER JOIN Customers AS C
    ON O.CustomerID =C.CustomerID

SELECT 
    P.ProductName,
    sum(O.Quantity) AS Total_Qty
FROM Orders AS O
INNER JOIN Products AS P
    ON O.ProductID = P.ProductID
GROUP  BY ProductName

SELECT 
    C.CustomerName,
    P.ProductName,
    C.Country,
    O.OrderDate
    
FROM Orders AS O
INNER JOIN Customers AS C
    ON O.CustomerID = C.CustomerID
INNER JOIN Products AS P
    ON O.ProductID = P.ProductID
WHERE C.Country IN ('UK','Canada')


SELECT
    C.CustomerName,
    O.OrderID,
    o.orderDate
FROM Customers AS C
LEFT JOIN Orders AS O
    ON O.CustomerID = C.CustomerID


SELECT
    P.Category,
    Sum(o.Quantity) AS Total_Qty
FROM Orders AS O
LEFT JOIN Products AS P
    ON O.ProductID = P.ProductID
GROUP BY P.Category


SELECT
    P.ProductName,
    ROUND(Sum(O.Quantity * P.Price),2) as Revenue
FROM Orders AS O
JOIN Products AS P
    ON O.ProductID = P.ProductID
GROUP BY p.ProductName
ORDER BY Revenue DESC



SELECT
    C.Country,
    COUNT(C.Country) As Order_By_Country
FROM Customers AS C
LEFT JOIN Orders AS O
    ON O.CustomerID = C.CustomerID
GROUP BY Country
HAVING COUNT(C.Country) > 1


use TWDP;
SELECT *
FROM Orders

SELECT *
FROM Products

SELECT *
FROM Customers



SELECT
    c.CustomerName,
    P.ProductName,
    ROUND(p.Price,2) AS Total_Price,
    ROUND(Sum(O.Quantity * P.Price),2) as Revenue
FROM Orders AS O
JOIN Products AS P
    ON O.ProductID = P.ProductID
JOIN Customers AS C
    ON O.CustomerID = C.CustomerID
GROUP BY p.ProductName, CustomerName,Price
ORDER BY Revenue DESC



SELECT
    *
FROM Customers AS C
FULL JOIN Orders AS O
    ON O.CustomerID = C.CustomerID
