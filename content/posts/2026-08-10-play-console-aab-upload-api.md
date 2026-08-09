---
title: "Play Console AAB 업로드 자동화 — Play Developer API 서비스 계정 설정과 403 PERMISSION_DENIED 해결"
slug: "play-console-aab-upload-api"
date: 2026-08-10T09:00:00+09:00
draft: false
tags: ["안드로이드", "PlayConsole", "PlayDeveloperAPI", "서비스계정", "자동화", "Flutter", "androidpublisher"]
categories: ["개발 인프라"]
description: "Google Play Console 에 앱 번들(AAB)을 브라우저 없이 올리는 방법. Cloud 프로젝트·서비스 계정·Play Console 권한 설정 4단계를 순서대로 적고, 권한을 줬는데도 403 PERMISSION_DENIED 가 나는 원인(읽기 권한 누락)까지 다룬다."
---

안드로이드 앱을 만들어 Play 비공개 테스트에 올리고 있다. 테스트 기간에는 빌드를
여러 번 올리게 되는데, 그때마다 막히는 자리가 하나 있었다.

**Play Console 의 「업로드」 버튼이다.**

브라우저는 프로그램이 만든 클릭으로는 파일 선택창을 열지 않는다. 사용자의 진짜
클릭이 있어야 한다. 보안 설계라 우회할 이유도 없고, 우회해서도 안 된다.

그래서 방향을 바꿨다. **선택창을 열지 않고 올리는 길**을 만들었다. Google 이
공식 API 를 제공한다.

## 만든 것

```
python tools/play_upload.py build/app/outputs/bundle/release/app-release.aab \
  --track alpha --notes "..."
```

```
[+] 인증 성공
[+] edit 12104050940855183802
    트랙 alpha: versionCodes=['67']
[+] 업로드 시작: app-release.aab (83.3 MB)
[+] 업로드 완료 — versionCode 68
[+] 트랙 alpha 에 배정
[✓] 커밋 완료 — alpha 트랙에 versionCode 68 출시
```

브라우저도, 사람 손도 필요 없다. CI 에 넣어도 되고 로컬에서 돌려도 된다.

## 준비 — 네 단계

한 번만 하면 된다. 문서가 여기저기 흩어져 있어서 순서대로 적는다.

### 1. Google Cloud 프로젝트를 만들고 API 를 켠다

Cloud Console 에서 프로젝트를 하나 만든다. 그다음 **Google Play Android Developer
API** 를 사용 설정한다.

> 예전에는 Play Console 과 Cloud 프로젝트를 **연결**하는 단계가 있었는데,
> 지금은 없어졌다. 공식 문서에 「이제 개발자 계정을 Google Cloud 프로젝트에
> 연결하지 않아도 됩니다」라고 명시돼 있다. Play Console 메뉴에서 「API 액세스」를
> 찾다가 못 찾는다면 그것 때문이다 — **없는 게 정상이다.**

### 2. 서비스 계정을 만든다

Cloud Console → IAM 및 관리자 → 서비스 계정 → 만들기.

GCP 역할(role)은 **하나도 줄 필요가 없다.** 권한은 Play Console 쪽에서 준다.
역할 선택 화면이 나오면 그냥 건너뛰고 완료하면 된다.

### 3. JSON 키를 받는다

만든 서비스 계정 → 키 → 키 추가 → 새 키 만들기 → **JSON**.

받는 즉시 **저장소 밖으로 옮긴다.** 나는 `~/.secrets/` 아래에 뒀다. 그리고
`.gitignore` 에 키 파일명 패턴을 넣어 뒀다 — 실수로 저장소에 떨어뜨렸을 때
커밋만은 막으려고.

```gitignore
play-uploader*.json
*-service-account*.json
```

### 4. Play Console 에서 권한을 준다

Play Console → **사용자 및 권한** → 신규 사용자 초대. 이메일 칸에 서비스 계정
주소를 넣는다(`...@....iam.gserviceaccount.com`).

권한은 **계정 권한** 탭에서 아래 둘을 켠다.

- **앱 정보 보기 및 보고서 일괄 다운로드(읽기 전용)**
- **앱을 테스트 트랙으로 출시**

프로덕션 출시 권한은 주지 않았다. 스크립트가 실수로 전체 공개를 눌러버릴 수 있는
경로 자체를 없애 두는 편이 낫다고 봤다. 프로덕션은 사람이 콘솔에서 한다.

> ⚠️ **읽기 권한을 빼먹으면 안 된다.** 「테스트 트랙으로 출시」만 켜면 최소 권한
> 원칙에는 맞아 보이는데, API 가 편집 세션을 만들 때 앱을 읽어야 해서 거부된다.
> 나는 여기서 반나절을 썼다. 아래에 따로 적는다.

## 스크립트가 하는 일

Play Developer API 는 **편집(edit) 단위**로 움직인다. 편집을 열고, 그 안에서
바꾸고, 마지막에 커밋하면 반영된다.

1. `edits` 를 만든다 → `editId`
2. `edits/{id}/bundles` 에 AAB 를 올린다 → `versionCode` 를 돌려준다
3. `edits/{id}/tracks/{track}` 에 그 버전을 배정한다
4. `edits/{id}:commit` 으로 확정한다

핵심은 마지막에 하나 더 있다.

```python
finally:
    if edit_id:
        s.delete(f"{BASE}/applications/{PACKAGE}/edits/{edit_id}")
```

**실패하면 편집을 버려야 한다.** 안 버리면 반쯤 만들어진 편집이 남고, 다음 실행이
「이미 진행 중인 편집이 있다」로 막힌다. 성공했을 때는 이미 커밋됐으니 지우지 않는다.

## 반나절 쓴 자리 — 403

권한을 주고 호출했더니 이렇게 나왔다.

```
[+] 인증 성공
[!] edit 생성 실패 (HTTP 403)
{
  "error": {
    "code": 403,
    "message": "The caller does not have permission",
    "status": "PERMISSION_DENIED"
  }
}
```

인증은 통과했다. 토큰은 받았다는 뜻이다. 권한만 거부됐다.

Play Console 에서 그 서비스 계정을 열어보니 상태가 **「활성」** 이었다. 권한도 준
대로 들어가 있었다. 그래서 **권한 전파가 아직 안 된 것**이라고 봤다. 구글 문서에도
최대 24시간 걸릴 수 있다고 적혀 있다.

30분짜리 재시도를 걸었다. 안 됐다. 6시간짜리를 걸고 잤다. 안 됐다.

원인은 시간이 아니라 **위에서 말한 읽기 권한 체크박스**였다. 그걸 켜자 같은 호출이
**즉시** 통과했다.

```
[+] edit 06179532489441590844
    트랙 production: versionCodes=-
    트랙 alpha: versionCodes=['67']
```

403 을 만나면 기다리기 전에 **권한 조합부터 다시 보는 편이 빠르다.** 오류 메시지가
「권한이 없다」고만 하고 무엇이 없는지 말하지 않으므로, 콘솔이 「활성」으로 보이는 것은
근거가 되지 못한다.

## 트랙 이름은 조회해서 쓴다

`--dry-run` 을 넣어 뒀다. 인증과 트랙 조회까지만 하고 아무것도 바꾸지 않는다.

```
$ python tools/play_upload.py --dry-run
[+] 인증 성공
    트랙 production: versionCodes=-
    트랙 beta: versionCodes=-
    트랙 alpha: versionCodes=['68']
    트랙 internal: versionCodes=-
```

콘솔에서 트랙 이름을 「Alpha」로 보이게 지어 놨어도 API 가 쓰는 이름은 `alpha` 다.
추측하지 말고 이렇게 한 번 찍어보고 쓰는 편이 안전하다.

## 곁다리 — 파일명은 버전을 말해주지 않는다

이 자동화를 붙이기 전에 손으로 올리다 이런 오류를 봤다.

```
error  rider-log-v63-UPLOAD_ME.aab
```

파일명은 `v63` 인데 실제 `versionCode` 는 **67** 이었다. 그리고 67 은 이미 올라가
있었으니 거부된 것이다. 이름을 붙인 시점과 빌드한 시점이 어긋난 채로 아무도 열어보지
않았다.

지금은 올리기 전에 매니페스트에서 직접 읽는다.

```bash
grep -o 'versionCode="[0-9]*"' \
  build/app/intermediates/merged_manifest/release/*/AndroidManifest.xml
# versionCode="68"
```

API 를 쓰면 이 문제가 대체로 사라진다. 빌드 산출물을 경로로 직접 넘기니 이름을
지을 일이 없다.

## 정리

- Play Console 에 「API 액세스」 메뉴가 없는 것은 정상이다. 연결 단계가 없어졌다
- GCP 역할은 필요 없다. 권한은 Play Console 의 **사용자 및 권한**에서 준다
- **읽기 권한 + 테스트 트랙 출시** 둘 다 있어야 한다. 하나만으로는 403 이 난다
- 실패하면 편집을 버려라. 안 그러면 다음 실행이 막힌다
- 트랙 이름은 조회해서 쓴다

빌드를 자주 올리는 단계라면 하루 안에 뽕을 뽑는다. 나는 이걸 붙인 날 바로 다음
빌드를 명령 한 줄로 올렸다.
