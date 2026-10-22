set -e
pkill -f "postgrest pgrst.conf" || true
bash "$(dirname "$0")/db_setup.sh" >/dev/null 2>&1
sudo -u postgres psql -q -d forume2e -c "insert into auth.users (id,email,raw_user_meta_data) values ('11111111-1111-1111-1111-111111111111','mina@example.com','{\"display_name\":\"MinaAndMochi\"}'),('22222222-2222-2222-2222-222222222222','joon@example.com','{\"display_name\":\"준이네\"}'),('33333333-3333-3333-3333-333333333333','owner@example.com','{\"display_name\":\"Owner\"}'); update public.profiles set role='admin' where id='33333333-3333-3333-3333-333333333333';"
(nohup /tmp/postgrest pgrst.conf > pgrst.log 2>&1 &); sleep 1.5
U1=$(python3 jwt.py authenticated 11111111-1111-1111-1111-111111111111 mina@example.com)
post(){ curl -sf -X POST localhost:8800/rest/v1/posts -H "Authorization: Bearer $U1" -H "Content-Type: application/json" -d "$1"; }
post '{"title":"Seoul to Jeju on Korean Air with a 6 kg Shih Tzu","body":"We flew GMP to CJU in July. The soft carrier fit under the seat and the check-in staff weighed the dog with the bag.\n\nTip: book the pet space by phone first.","transport":"plane_cabin","species":"dog","breed":"Shih Tzu","weight":"w5_8","carrier":"soft_bag","weather":"hot","season":"summer","airline_slug":"korean-air","operator":"Korean Air","route_from":"Seoul (GMP)","route_to":"Jeju","trip_date":"2026-07-01","lang":"en"}'
post '{"title":"고양이 두 마리와 KTX 부산 여행","body":"고양이 두 마리를 하드 켄넬에 넣고 KTX를 탔어요. 승무원분들이 친절했고 소리도 거의 안 냈어요. 시발역인 서울역에서 출발했어요.","transport":"train","species":"cat","weight":"w_lt5","carrier":"hard_crate","season":"autumn","weather":"mild","operator":"Korail KTX","route_from":"서울","route_to":"부산","lang":"ko"}'
post '{"title":"Cheap pet taxi","body":"Book now at https://spam.example.com cheapest pet taxi in Seoul!!! casino bonus","transport":"taxi","species":"dog"}'
post '{"title":"Hold travel in winter","body":"Our lab flew in the hold from Incheon to Paris in January; the crate needed zip ties and absorbent pads.","transport":"plane_hold","species":"dog","weight":"w25_40","carrier":"hard_crate","weather":"cold","season":"winter","airline_slug":"air-france","lang":"en"}'
export SUPABASE_URL=http://localhost:8800 SUPABASE_SERVICE_ROLE_KEY=$(python3 jwt.py service_role)
cd /workspace/petsite-forum
for id in $(python3 forum/moderate.py list | python3 -c "import json,sys;[print(i['id']) for i in json.load(sys.stdin)['items']]"); do python3 forum/moderate.py set post $id published "ok" >/dev/null; done
python3 build.py 2>&1 | grep -i "forum\|warn"
