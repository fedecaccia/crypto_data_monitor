for filename in orderbook/*.csv; do
    awk '{if (!($0 in x)) {print $0; x[$0]=1} }' "$filename" > "orderbook_fixed/$(basename "$filename" .csv).csv"
done