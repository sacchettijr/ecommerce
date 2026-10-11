# Business Calculations

No non-trivial business calculations exist in the codebase as of this
writing.

The only numeric business rule found is `ProductModel.price`, a plain
`DecimalField` validated by `utils.validator.validate_positive_decimal`
(must be strictly greater than zero). There is no tax, discount, shipping
cost, subtotal/total, or currency-conversion computation anywhere in the
backend or frontend — consistent with there being no shopping cart or
checkout flow (see `domain.md`).

If pricing, tax, or cart-total logic is added in the future, document the
formula and its source file(s) here rather than leaving it implicit in
code.
