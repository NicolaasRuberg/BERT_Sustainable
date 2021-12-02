#/bin/bash
for value in $1/*.pdf
do
   echo "####"
   echo $value
   echo "python xtract.py -f $value -o $2/$(basename -s .pdf $value ).jsonl"
   echo "####"
   python xtract.py -f $value -o "$1/$(basename -s .pdf $value ).jsonl"
done
