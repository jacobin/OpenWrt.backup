suburl=`url_encode "%1"`
outFileName=%2

## https://stackoverflow.com/questions/7729023/how-do-i-break-up-an-extremely-long-string-literal-in-bash
suburl2="http://127.0.0.1:25500/sub?target=clash&config=ACL4SSR_Online_Full_Adb"`
        `"lockPlus.ini&enable_filter=true&filter_script=function%20filter%28nod"`
        `"e%29%20%7B%0A%20%20%20%20if%28node.Type.toLowerCase%28%29%20%3D%3D%3D"`
        `"%20%22ss%22%20%26%26%20node.EncryptMethod.toLowerCase%28%29%20%3D%3D%"`
        `"3D%20%22chacha20-poly1305%22%29%20%7B%0A%20%20%20%20%20%20%20%20retur"`
        `"n%20false%3B%0A%20%20%20%20%7D%0A%20%20%20%20return%20true%3B%0A%7D&e"`
        `"xclude=%28%E4%B8%AD%E5%9C%8B%7C%E9%A6%99%E6%B8%AF%7C%E4%B8%AD%E5%9B%B"`
        `"D%7CCN%7CHK%7CHong%20Kong%7CHongKong%7C%E5%B9%BF%E4%B8%9C%7C%E8%B4%B5"`
        `"%E5%B7%9E%7C%E5%8C%97%E4%BA%AC%7C%E4%B8%8A%E6%B5%B7%7C%E7%A7%BB%E5%8A"`
        `"%A8%7Cv2cross%29&append_type=true&emoji=true&list=false&udp=true&tfo="`
        `"true&scv=true&fdn=true"
suburl="$suburl2""&url=""$suburl"

wget "$suburl" -OnodesTmp.yaml

if [[ -z $(grep '[^[:space:]]' nodesTmp.yaml) ]] ; then
    echo "No nodes are downloaded"
    exit 3
fi

rm wpage.txt
rm onlysubs.txt

rm "$outFileName"
mv nodesTmp.yaml "$outFileName"
