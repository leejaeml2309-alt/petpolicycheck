-- Seed list for the instant keyword pre-filter (public.moderation_terms).
-- Edit freely in Supabase Table Editor > moderation_terms (enable/disable rows, add terms).
-- 'reject' = rejected at insert; 'flag' = hidden and queued first for the moderator.
-- Korean terms use 'substring' (particles attach to words); Latin terms use whole-word matching.
-- Keep the list conservative: anything that could appear in an honest travel report
-- (country names, "government", "rules", a dog called 토토 ...) is 'flag' or left out.
insert into public.moderation_terms (term, lang, category, action, match_mode) values
-- links / contact spam -> flag for review
('(https?://|www\.)', 'any', 'link', 'flag', 'regex'),
('open\.kakao', 'any', 'link', 'flag', 'regex'),
('telegram', 'en', 'spam', 'flag', 'word'),
('whatsapp', 'en', 'spam', 'flag', 'word'),
('텔레그램', 'ko', 'spam', 'flag', 'substring'),
('오픈채팅', 'ko', 'spam', 'flag', 'substring'),
('카톡 아이디', 'ko', 'spam', 'flag', 'substring'),
-- commercial spam
('casino', 'en', 'spam', 'reject', 'word'),
('viagra', 'en', 'spam', 'reject', 'word'),
('cialis', 'en', 'spam', 'reject', 'word'),
('bitcoin', 'en', 'spam', 'flag', 'word'),
('crypto', 'en', 'spam', 'flag', 'word'),
('forex', 'en', 'spam', 'reject', 'word'),
('payday loan', 'en', 'spam', 'reject', 'word'),
('escort service', 'en', 'spam', 'reject', 'word'),
('카지노', 'ko', 'spam', 'reject', 'substring'),
('바카라', 'ko', 'spam', 'reject', 'substring'),
('먹튀', 'ko', 'spam', 'reject', 'substring'),
('토토사이트', 'ko', 'spam', 'reject', 'substring'),
('토토', 'ko', 'spam', 'flag', 'substring'),
('대출', 'ko', 'spam', 'flag', 'substring'),
('코인 리딩', 'ko', 'spam', 'reject', 'substring'),
-- slurs / hate (EN)
('nigger', 'en', 'slur', 'reject', 'word'), ('niggers', 'en', 'slur', 'reject', 'word'),
('nigga', 'en', 'slur', 'reject', 'word'), ('faggot', 'en', 'slur', 'reject', 'word'),
('fag', 'en', 'slur', 'reject', 'word'), ('retard', 'en', 'slur', 'reject', 'word'),
('retarded', 'en', 'slur', 'reject', 'word'), ('kike', 'en', 'slur', 'reject', 'word'),
('spic', 'en', 'slur', 'reject', 'word'), ('chink', 'en', 'slur', 'reject', 'word'),
('gook', 'en', 'slur', 'reject', 'word'), ('tranny', 'en', 'slur', 'reject', 'word'),
('cunt', 'en', 'slur', 'reject', 'word'), ('whore', 'en', 'slur', 'reject', 'word'),
('slut', 'en', 'slur', 'reject', 'word'),
-- profanity (EN) -> flag (could be venting about a bad trip; the moderator decides)
('fuck', 'en', 'other', 'flag', 'word'), ('fucking', 'en', 'other', 'flag', 'word'),
('shit', 'en', 'other', 'flag', 'word'), ('bitch', 'en', 'other', 'flag', 'word'),
('asshole', 'en', 'other', 'flag', 'word'),
-- slurs / hate / insults (KO)
('씨발', 'ko', 'slur', 'reject', 'substring'), ('씨바', 'ko', 'slur', 'reject', 'substring'),
('시발($|[^점역])', 'ko', 'slur', 'reject', 'regex'),   -- not 시발점/시발역 (starting point/station)
('ㅅㅂ', 'ko', 'slur', 'reject', 'substring'), ('ㅆㅂ', 'ko', 'slur', 'reject', 'substring'),
('병신', 'ko', 'slur', 'reject', 'substring'), ('ㅂㅅ', 'ko', 'slur', 'flag', 'substring'),
('개새끼', 'ko', 'slur', 'reject', 'substring'), ('개새기', 'ko', 'slur', 'reject', 'substring'),
('좆', 'ko', 'slur', 'reject', 'substring'), ('니미', 'ko', 'slur', 'flag', 'substring'),
('느금마', 'ko', 'slur', 'reject', 'substring'), ('엠창', 'ko', 'slur', 'reject', 'substring'),
('한남충', 'ko', 'slur', 'reject', 'substring'), ('김치녀', 'ko', 'slur', 'reject', 'substring'),
('된장녀', 'ko', 'slur', 'reject', 'substring'), ('틀딱', 'ko', 'slur', 'reject', 'substring'),
('짱깨', 'ko', 'slur', 'reject', 'substring'), ('쪽바리', 'ko', 'slur', 'reject', 'substring'),
('애자', 'ko', 'slur', 'flag', 'substring'), ('장애새끼', 'ko', 'slur', 'reject', 'substring'),
('존나', 'ko', 'other', 'flag', 'substring'), ('미친놈', 'ko', 'other', 'flag', 'substring'),
('미친년', 'ko', 'slur', 'reject', 'substring'),
-- slurs / insults (FR)
('connard', 'fr', 'slur', 'reject', 'word'), ('connasse', 'fr', 'slur', 'reject', 'word'),
('salope', 'fr', 'slur', 'reject', 'word'), ('pute', 'fr', 'slur', 'reject', 'word'),
('enculé', 'fr', 'slur', 'reject', 'word'), ('encule', 'fr', 'slur', 'reject', 'word'),
('pédé', 'fr', 'slur', 'reject', 'word'), ('bougnoule', 'fr', 'slur', 'reject', 'word'),
('youpin', 'fr', 'slur', 'reject', 'word'), ('fils de pute', 'fr', 'slur', 'reject', 'word'),
('putain', 'fr', 'other', 'flag', 'word'), ('ta gueule', 'fr', 'other', 'flag', 'word'),
-- violence / self-harm
('kill yourself', 'en', 'violence', 'reject', 'word'), ('kys', 'en', 'violence', 'reject', 'word'),
('i will kill you', 'en', 'violence', 'reject', 'word'),
('죽여버', 'ko', 'violence', 'reject', 'substring'), ('자살해', 'ko', 'violence', 'reject', 'substring'),
('죽어라', 'ko', 'violence', 'flag', 'substring'),
('crève', 'fr', 'violence', 'flag', 'word'),
-- NSFW
('porn', 'en', 'nsfw', 'reject', 'word'), ('porno', 'en', 'nsfw', 'reject', 'word'),
('xxx', 'en', 'nsfw', 'reject', 'word'), ('nudes', 'en', 'nsfw', 'reject', 'word'),
('onlyfans', 'en', 'nsfw', 'reject', 'word'), ('hentai', 'en', 'nsfw', 'reject', 'word'),
('blowjob', 'en', 'nsfw', 'reject', 'word'), ('sex', 'en', 'nsfw', 'flag', 'word'),
('sexe', 'fr', 'nsfw', 'flag', 'word'),
('야동', 'ko', 'nsfw', 'reject', 'substring'), ('섹스', 'ko', 'nsfw', 'reject', 'substring'),
('포르노', 'ko', 'nsfw', 'reject', 'substring'), ('자위', 'ko', 'nsfw', 'flag', 'substring'),
('보지', 'ko', 'nsfw', 'flag', 'substring'),   -- flag only: also in 보지 못했다 ("did not see")
('자지', 'ko', 'nsfw', 'flag', 'substring'),
('조건만남', 'ko', 'nsfw', 'reject', 'substring'), ('성인방송', 'ko', 'nsfw', 'reject', 'substring'),
-- politics (EN)
('trump', 'en', 'politics', 'reject', 'word'), ('biden', 'en', 'politics', 'reject', 'word'),
('kamala', 'en', 'politics', 'reject', 'word'), ('obama', 'en', 'politics', 'reject', 'word'),
('maga', 'en', 'politics', 'reject', 'word'), ('democrats', 'en', 'politics', 'reject', 'word'),
('republicans', 'en', 'politics', 'reject', 'word'), ('gop', 'en', 'politics', 'reject', 'word'),
('election', 'en', 'politics', 'reject', 'word'), ('impeachment', 'en', 'politics', 'reject', 'word'),
('putin', 'en', 'politics', 'reject', 'word'), ('zelensky', 'en', 'politics', 'reject', 'word'),
('netanyahu', 'en', 'politics', 'reject', 'word'), ('hamas', 'en', 'politics', 'reject', 'word'),
('kim jong un', 'en', 'politics', 'reject', 'word'), ('xi jinping', 'en', 'politics', 'reject', 'word'),
('left-wing', 'en', 'politics', 'flag', 'word'), ('right-wing', 'en', 'politics', 'flag', 'word'),
-- politics (FR)
('macron', 'fr', 'politics', 'reject', 'word'), ('le pen', 'fr', 'politics', 'reject', 'word'),
('mélenchon', 'fr', 'politics', 'reject', 'word'), ('melenchon', 'fr', 'politics', 'reject', 'word'),
('bardella', 'fr', 'politics', 'reject', 'word'), ('rassemblement national', 'fr', 'politics', 'reject', 'word'),
('élection', 'fr', 'politics', 'reject', 'word'), ('élections', 'fr', 'politics', 'reject', 'word'),
-- politics (KO)
('윤석열', 'ko', 'politics', 'reject', 'substring'), ('이재명', 'ko', 'politics', 'reject', 'substring'),
('문재인', 'ko', 'politics', 'reject', 'substring'), ('박근혜', 'ko', 'politics', 'reject', 'substring'),
('한동훈', 'ko', 'politics', 'reject', 'substring'), ('김정은', 'ko', 'politics', 'reject', 'substring'),
('국민의힘', 'ko', 'politics', 'reject', 'substring'), ('더불어민주당', 'ko', 'politics', 'reject', 'substring'),
('민주당', 'ko', 'politics', 'reject', 'substring'), ('정의당', 'ko', 'politics', 'reject', 'substring'),
('조국혁신당', 'ko', 'politics', 'reject', 'substring'), ('개혁신당', 'ko', 'politics', 'reject', 'substring'),
('탄핵', 'ko', 'politics', 'reject', 'substring'), ('대선', 'ko', 'politics', 'reject', 'substring'),
('총선', 'ko', 'politics', 'reject', 'substring'), ('빨갱이', 'ko', 'politics', 'reject', 'substring'),
('좌파', 'ko', 'politics', 'flag', 'substring'), ('우파', 'ko', 'politics', 'flag', 'substring'),
('일베', 'ko', 'politics', 'reject', 'substring'), ('대깨문', 'ko', 'politics', 'reject', 'substring'),
('수꼴', 'ko', 'politics', 'reject', 'substring'), ('좌좀', 'ko', 'politics', 'reject', 'substring'),
('대통령', 'ko', 'politics', 'flag', 'substring')
on conflict (term, match_mode) do nothing;
