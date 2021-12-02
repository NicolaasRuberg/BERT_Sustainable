#/bin/bash
for value in $1/*.xlsx
do
   echo "####"
   echo "python convertGRI_xls_json.py -f $value -o $2/$(basename -s .pdf $value ).jsonl"
   python convertGRI_xls_json.py -f $value -o $2/$(basename -s .xlsx $value ).jsonl
done
