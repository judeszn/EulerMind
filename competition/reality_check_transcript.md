# Σ3 Phase 1 — Reality Check transcript

Model: `model/Qwen2.5-Math-1.5B-Instruct-Q4_K_M.gguf` · questions: 12 · Derived: 7 · Heuristic: 5 · Truncated: 0 · mean 7.7s/question · **False verifications: 0** (must be 0)

> Phase 2 audit question for every explanation below: *Could a struggling SS2/SS3 student genuinely understand this?* If not, note exactly why (skipped reasoning / too symbolic / assumes prior knowledge / poor ordering / too verbose / too short).

## Q1. Solve 2x^2 + 7x + 3 = 0. Show your working.
*label:* **Derived** · *8.0s* · *check:* all 2 given root(s) substitute correctly (completeness not verified)

```
To solve the quadratic equation \(2x^2 + 7x + 3 = 0\), we can use the quadratic formula, which is given by:

\[x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}\]

Here, the coefficients are \(a = 2\), \(b = 7\), and \(c = 3\). Let's substitute these values into the quadratic formula.

First, we calculate the discriminant:

\[b^2 - 4ac = 7^2 - 4 \cdot 2 \cdot 3 = 49 - 24 = 25\]

Next, we substitute the discriminant and the coefficients into the quadratic formula:

\[x = \frac{-7 \pm \sqrt{25}}{2 \cdot 2} = \frac{-7 \pm 5}{4}\]

This gives us two solutions:

\[x = \frac{-7 + 5}{4} = \frac{-2}{4} = -\frac{1}{2}\]

and

\[x = \frac{-7 - 5}{4} = \frac{-12}{4} = -3\]

So, the solutions to the equation \(2x^2 + 7x + 3 = 0\) are:

\[\boxed{-\frac{1}{2}, -3}\]
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q2. Solve the simultaneous equations 3x + 2y = 16 and x - y = 3.
*label:* **Derived** · *13.2s* · *check:* (x=4.4, y=1.4) satisfies both equations

```
To solve the simultaneous equations \(3x + 2y = 16\) and \(x - y = 3\), we can use the method of substitution or elimination. Here, we will use the elimination method.

First, let's write down the equations:
1. \(3x + 2y = 16\)
2. \(x - y = 3\)

We can eliminate one of the variables by making the coefficients of \(y\) in both equations the same. To do this, we can multiply the second equation by 2:
\[2(x - y) = 2 \cdot 3\]
\[2x - 2y = 6\]

Now we have the system:
1. \(3x + 2y = 16\)
2. \(2x - 2y = 6\)

Next, we add the two equations together to eliminate \(y\):
\[
(3x + 2y) + (2x - 2y) = 16 + 6
\]
\[
3x + 2x + 2y - 2y = 22
\]
\[
5x = 22
\]
\[
x = \frac{22}{5}
\]

Now that we have \(x\), we can substitute it back into one of the original equations to find \(y\). Let's use the second equation \(x - y = 3\):
\[
\frac{22}{5} - y = 3
\]
To isolate \(y\), we first subtract \(\frac{22}{5}\) from both sides:
\[
-y = 3 - \frac{22}{5}
\]
To combine the terms on the right side, we need a common denominator:
\[
3 = \frac{15}{5}
\]
So,
\[
-y = \frac{15}{5} - \frac{22}{5}
\]
\[
-y = \frac{15 - 22}{5}
\]
\[
-y = \frac{-7}{5}
\]
\[
y = \frac{7}{5}
\]

Therefore, the solution to the system of equations is:
\[
\boxed{\left( \frac{22}{5}, \frac{7}{5} \right)}
\]
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q3. Solve 5x - 7 = 2x + 8.
*label:* **Derived** · *8.5s* · *check:* all 1 given root(s) substitute correctly (completeness not verified)

```
To solve the equation \(5x - 7 = 2x + 8\), we will follow a step-by-step approach:

1. **Isolate the variable terms on one side of the equation:**
   We start by getting all the \(x\)-terms on one side and the constant terms on the other side. To do this, we can subtract \(2x\) from both sides of the equation:
   \[
   5x - 7 - 2x = 2x + 8 - 2x
   \]
   Simplifying both sides, we get:
   \[
   3x - 7 = 8
   \]

2. **Isolate the variable term:**
   Next, we need to get rid of the constant term \(-7\) on the left side. We do this by adding 7 to both sides of the equation:
   \[
   3x - 7 + 7 = 8 + 7
   \]
   Simplifying both sides, we get:
   \[
   3x = 15
   \]

3. **Solve for \(x\):**
   Now, we need to isolate \(x\) by dividing both sides of the equation by 3:
   \[
   \frac{3x}{3} = \frac{15}{3}
   \]
   Simplifying both sides, we get:
   \[
   x = 5
   \]

So, the solution to the equation \(5x - 7 = 2x + 8\) is \(\boxed{5}\).
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q4. Expand (2x - 3)(x + 5).
*label:* **Derived** · *7.9s* · *check:* matches the original expression at 5 sample points

```
To expand the expression \((2x - 3)(x + 5)\), we will use the distributive property, which states that \(a(b + c) = ab + ac\). Here, we will distribute each term in the first binomial to each term in the second binomial.

Let's break it down step by step:

1. Distribute \(2x\) to both \(x\) and \(5\):
   \[
   2x \cdot x + 2x \cdot 5 = 2x^2 + 10x
   \]

2. Distribute \(-3\) to both \(x\) and \(5\):
   \[
   -3 \cdot x + (-3) \cdot 5 = -3x - 15
   \]

3. Combine the results from the two distributions:
   \[
   2x^2 + 10x - 3x - 15
   \]

4. Combine like terms (the \(x\) terms):
   \[
   2x^2 + (10x - 3x) - 15 = 2x^2 + 7x - 15
   \]

So, the expanded form of \((2x - 3)(x + 5)\) is \(\boxed{2x^2 + 7x - 15}\).
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q5. Factorise x^2 - 5x + 6.
*label:* **Derived** · *7.2s* · *check:* matches the original expression at 5 sample points

```
To factorise the quadratic expression \(x^2 - 5x + 6\), we need to find two numbers that multiply to give the constant term (6) and add up to give the coefficient of the linear term (-5).

Let's find these two numbers:
1. We need two numbers that multiply to 6.
2. We need these same two numbers to add up to -5.

Let's list the pairs of factors of 6:
- 1 and 6
- 2 and 3
- -1 and -6
- -2 and -3

Now, let's check which pair adds up to -5:
- 1 + 6 = 7
- 2 + 3 = 5
- -1 + (-6) = -7
- -2 + (-3) = -5

The pair -2 and -3 adds up to -5. Therefore, we can write the quadratic expression as:
\[x^2 - 5x + 6 = (x - 2)(x - 3)\]

So, the factorized form of \(x^2 - 5x + 6\) is \(\boxed{(x - 2)(x - 3)}\).
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q6. Simplify 3(2x - 1) + 4(x + 2).
*label:* **Derived** · *5.5s* · *check:* matches the original expression at 5 sample points

```
To simplify the expression \(3(2x - 1) + 4(x + 2)\), we will follow these steps:

1. Distribute the constants 3 and 4 to the terms inside the parentheses.
2. Combine like terms.

Let's start with the distribution:

\[3(2x - 1) + 4(x + 2) = 3 \cdot 2x + 3 \cdot (-1) + 4 \cdot x + 4 \cdot 2\]

This simplifies to:

\[6x - 3 + 4x + 8\]

Next, we combine the like terms. The like terms here are the \(x\) terms and the constant terms:

\[6x + 4x - 3 + 8 = (6x + 4x) + (-3 + 8) = 10x + 5\]

So, the simplified expression is:

\[\boxed{10x + 5}\]
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q7. Differentiate y = x^3 - 4x^2 + 2x with respect to x.
*label:* **Derived** · *8.5s* · *check:* claimed derivative matches numeric differentiation at 5 sample points

```
To differentiate the function \( y = x^3 - 4x^2 + 2x \) with respect to \( x \), we will apply the power rule of differentiation. The power rule states that if \( y = x^n \), then \( \frac{dy}{dx} = nx^{n-1} \).

Let's differentiate each term in the function \( y = x^3 - 4x^2 + 2x \) separately.

1. Differentiate \( x^3 \):
   \[
   \frac{d}{dx}(x^3) = 3x^{3-1} = 3x^2
   \]

2. Differentiate \( -4x^2 \):
   \[
   \frac{d}{dx}(-4x^2) = -4 \cdot 2x^{2-1} = -8x
   \]

3. Differentiate \( 2x \):
   \[
   \frac{d}{dx}(2x) = 2 \cdot 1x^{1-1} = 2
   \]

Now, combine the derivatives of each term to get the derivative of the entire function:
\[
\frac{dy}{dx} = 3x^2 - 8x + 2
\]

Thus, the derivative of \( y = x^3 - 4x^2 + 2x \) with respect to \( x \) is \(\boxed{3x^2 - 8x + 2}\).
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q8. Evaluate 15% of 240.
*label:* **Heuristic** · *4.4s* · *check:* question shape not in the checkable families

```
To evaluate 15% of 240, we can follow these steps:

1. Convert the percentage to a decimal. Since 15% means 15 per 100, we can write it as:
   \[
   15\% = \frac{15}{100} = 0.15
   \]

2. Multiply the decimal by 240 to find 15% of 240:
   \[
   0.15 \times 240
   \]

3. Perform the multiplication:
   \[
   0.15 \times 240 = 36
   \]

So, 15% of 240 is \boxed{36}.
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q9. Make x the subject of the formula v = u + a*x.
*label:* **Heuristic** · *4.4s* · *check:* question shape not in the checkable families

```
To solve the equation \( v = u + a \cdot x \) for \( x \), we will follow these steps:

1. **Isolate the term involving \( x \)**:
   \[
   v = u + a \cdot x
   \]
   Subtract \( u \) from both sides to isolate the term with \( x \):
   \[
   v - u = a \cdot x
   \]

2. **Solve for \( x \)**:
   Divide both sides by \( a \) to solve for \( x \):
   \[
   x = \frac{v - u}{a}
   \]

Thus, the solution for \( x \) is:
\[
\boxed{x = \frac{v - u}{a}}
\]
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q10. A trader buys an item for 4500 naira and sells it for 5400 naira. Find the percentage profit.
*label:* **Heuristic** · *7.8s* · *check:* question shape not in the checkable families

```
To find the percentage profit, we need to follow these steps:

1. Determine the profit by subtracting the cost price from the selling price.
2. Calculate the percentage profit by dividing the profit by the cost price and then multiplying by 100.

Let's go through each step in detail:

1. **Calculate the profit:**
   The cost price (CP) is 4500 nairas and the selling price (SP) is 5400 nairas.
   \[
   \text{Profit} = \text{SP} - \text{CP} = 5400 - 4500 = 900 \text{ nairas}
   \]

2. **Calculate the percentage profit:**
   The percentage profit is given by the formula:
   \[
   \text{Percentage Profit} = \left( \frac{\text{Profit}}{\text{CP}} \right) \times 100
   \]
   Substituting the values we have:
   \[
   \text{Percentage Profit} = \left( \frac{900}{4500} \right) \times 100 = \left( \frac{1}{5} \right) \times 100 = 20\%
   \]

Therefore, the percentage profit is \boxed{20}.
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q11. Find the gradient of the line joining the points (1, 2) and (4, 11).
*label:* **Heuristic** · *7.7s* · *check:* question shape not in the checkable families

```
To find the gradient of the line joining the points \((1, 2)\) and \((4, 11)\), we use the formula for the gradient (or slope) of a line passing through two points \((x_1, y_1)\) and \((x_2, y_2)\):

\[
\text{梯度} = \frac{y_2 - y_1}{x_2 - x_1}
\]

Here, the points are \((1, 2)\) and \((4, 11)\). Let's identify the coordinates:
- \(x_1 = 1\)
- \(y_1 = 2\)
- \(x_2 = 4\)
- \(y_2 = 11\)

Now, substitute these values into the formula:

\[
\text{梯度} = \frac{11 - 2}{4 - 1}
\]

Calculate the numerator and the denominator:

\[
11 - 2 = 9
\]
\[
4 - 1 = 3
\]

So, the gradient is:

\[
\text{梯度} = \frac{9}{3} = 3
\]

Therefore, the gradient of the line joining the points \((1, 2)\) and \((4, 11)\) is \(\boxed{3}\).
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---

## Q12. Prove that the sum of the angles in a triangle is 180 degrees.
*label:* **Heuristic** · *9.5s* · *check:* question shape not in the checkable families

```
To prove that the sum of the angles in a triangle is 180 degrees, we can use the properties of parallel lines and the angles formed when a transversal intersects them. Here is a step-by-step proof:

1. **Draw a Triangle and a Parallel Line:**
   Consider a triangle \(ABC\). Draw a line through point \(A\) that is parallel to line \(BC\). Let's call this line \(DE\), where \(D\) is on \(AB\) and \(E\) is on \(AC\).

2. **Identify Corresponding Angles:**
   Since \(DE\) is parallel to \(BC\) and \(AB\) and \(AC\) are transversals, the corresponding angles are equal. Therefore, \(\angle DAB = \angle ABC\) (corresponding angles) and \(\angle EAC = \angle ACB\) (corresponding angles).

3. **Sum of Angles on a straight line:**
   The angles on a straight line sum up to 180 degrees. So, \(\angle DAB + \angle BAC + \angle EAC = 180^\circ\).

4. **Substitute the Corresponding Angles:**
   Since \(\angle DAB = \angle ABC\) and \(\angle EAC = \angle ACB\), we can substitute these into the equation:
   \[
   \angle ABC + \angle BAC + \angle ACB = 180^\circ
   \]
   This shows that the sum of the angles in triangle \(ABC\) is 180 degrees.

Therefore, the sum of the angles in a triangle is \(\boxed{180}\) degrees.
```

Audit — understandable to a struggling SS3 student? __________  why / why not: __________

---
