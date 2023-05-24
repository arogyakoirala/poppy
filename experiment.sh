declare -a Cutoffs=("0" "0.2" "0.4" "0.6" "0.8")
declare -a Masks=("0" "60" "65" "70" "75" "80" "85" "90" "95")


for cutoff in "${Cutoffs[@]}"; do
    for mask in "${Masks[@]}"; do
        echo "Cutoff:" $cutoff
        echo "Mask %:" $mask
    done
done
