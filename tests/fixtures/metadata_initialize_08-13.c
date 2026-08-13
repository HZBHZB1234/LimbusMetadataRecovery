char sub_18069C5E0()
{
  __int64 v0; // rax
  __int64 v1; // rax
  __int64 v2; // rcx
  __int64 v3; // rdx
  unsigned __int64 v4; // r8
  __int128 v5; // xmm0
  __int64 v6; // rdx
  unsigned __int64 v7; // rdx
  unsigned __int64 v8; // rdx
  unsigned __int64 v9; // rdx
  unsigned __int64 v10; // rdx
  unsigned __int64 v11; // rdx
  __int64 v12; // rcx
  __int64 v13; // rax
  __int64 v14; // rdi
  __int64 v15; // rbx
  unsigned __int64 v16; // r8
  unsigned __int64 i; // rdx
  __int64 v18; // rax
  __int64 v19; // rdi
  __int64 v20; // rbx
  unsigned __int64 v21; // r8
  __int64 j; // rdx
  __int64 v23; // rax
  __int64 v24; // rdi
  __int64 v25; // rbx
  unsigned __int64 v26; // r8
  unsigned __int64 k; // rdx
  __int64 v28; // rax
  __int64 v29; // rdi
  __int64 v30; // rbx
  unsigned __int64 v31; // r8
  unsigned __int64 m; // rdx
  __int64 v33; // rax
  __int64 v34; // rdi
  __int64 v35; // rbx
  unsigned __int64 v36; // r8
  unsigned __int64 n; // rdx
  __int64 v38; // rax
  __int64 v39; // rdi
  __int64 v40; // rbx
  unsigned __int64 v41; // r8
  __int64 ii; // rdx
  __int64 v43; // rax
  _DWORD *v44; // rbx
  __int64 v45; // rdi
  unsigned __int64 v46; // r8
  unsigned __int64 jj; // rdx
  __int64 v48; // r9
  int v49; // edx
  int v50; // eax
  int v51; // ecx
  int v52; // edx
  int v53; // r8d
  int v54; // r10d
  int v55; // edx
  int v56; // r10d
  char v58[32]; // [rsp+20h] [rbp-28h] BYREF

  strcpy(v58, "global-metadata.dat");
  v0 = sub_180693580(v58);
  qword_187E57E38 = v0;
  if ( v0 )
  {
    v1 = ((__int64 (__fastcall *)(__int64))sub_18072F9A0)(1236);
    v2 = qword_187E57E38;
    qword_187E57E58 = v1;
    v3 = v1;
    v4 = 9;
    do
    {
      v3 += 128;
      v5 = *(_OWORD *)v2;
      v2 += 128;
      *(_OWORD *)(v3 - 128) = v5;
      *(_OWORD *)(v3 - 112) = *(_OWORD *)(v2 - 112);
      *(_OWORD *)(v3 - 96) = *(_OWORD *)(v2 - 96);
      *(_OWORD *)(v3 - 80) = *(_OWORD *)(v2 - 80);
      *(_OWORD *)(v3 - 64) = *(_OWORD *)(v2 - 64);
      *(_OWORD *)(v3 - 48) = *(_OWORD *)(v2 - 48);
      *(_OWORD *)(v3 - 32) = *(_OWORD *)(v2 - 32);
      *(_OWORD *)(v3 - 16) = *(_OWORD *)(v2 - 16);
      --v4;
    }
    while ( v4 );
    *(_OWORD *)v3 = *(_OWORD *)v2;
    *(_OWORD *)(v3 + 16) = *(_OWORD *)(v2 + 16);
    *(_OWORD *)(v3 + 32) = *(_OWORD *)(v2 + 32);
    *(_OWORD *)(v3 + 48) = *(_OWORD *)(v2 + 48);
    *(_OWORD *)(v3 + 64) = *(_OWORD *)(v2 + 64);
    *(_DWORD *)(v3 + 80) = *(_DWORD *)(v2 + 80);
    v6 = 0x30FBE73A8992293ELL;
    do
    {
      v7 = v6
         ^ (v6 << 13)
         ^ ((v6 ^ (unsigned __int64)(v6 << 13)) >> 7)
         ^ ((v6 ^ (v6 << 13) ^ ((v6 ^ (unsigned __int64)(v6 << 13)) >> 7)) << 17);
      *(_BYTE *)(v4 + v1) ^= byte_187355000[(unsigned __int8)(v7 ^ BYTE1(v7) ^ BYTE2(v7) ^ BYTE3(v7))];
      v8 = v7 ^ (v7 << 13) ^ ((v7 ^ (v7 << 13)) >> 7) ^ ((v7 ^ (v7 << 13) ^ ((v7 ^ (v7 << 13)) >> 7)) << 17);
      *(_BYTE *)(v4 + v1 + 1) ^= byte_187355000[(unsigned __int8)(v8 ^ BYTE1(v8) ^ BYTE2(v8) ^ BYTE3(v8))];
      v9 = v8 ^ (v8 << 13) ^ ((v8 ^ (v8 << 13)) >> 7) ^ ((v8 ^ (v8 << 13) ^ ((v8 ^ (v8 << 13)) >> 7)) << 17);
      *(_BYTE *)(v4 + v1 + 2) ^= byte_187355000[(unsigned __int8)(v9 ^ BYTE1(v9) ^ BYTE2(v9) ^ BYTE3(v9))];
      v10 = v9 ^ (v9 << 13) ^ ((v9 ^ (v9 << 13)) >> 7) ^ ((v9 ^ (v9 << 13) ^ ((v9 ^ (v9 << 13)) >> 7)) << 17);
      *(_BYTE *)(v4 + v1 + 3) ^= byte_187355000[(unsigned __int8)(v10 ^ BYTE1(v10) ^ BYTE2(v10) ^ BYTE3(v10))];
      v11 = v10 ^ (v10 << 13) ^ ((v10 ^ (v10 << 13)) >> 7) ^ ((v10 ^ (v10 << 13) ^ ((v10 ^ (v10 << 13)) >> 7)) << 17);
      *(_BYTE *)(v4 + v1 + 4) ^= byte_187355000[(unsigned __int8)(v11 ^ BYTE1(v11) ^ BYTE2(v11) ^ BYTE3(v11))];
      v6 = v11 ^ (v11 << 13) ^ ((v11 ^ (v11 << 13)) >> 7) ^ ((v11 ^ (v11 << 13) ^ ((v11 ^ (v11 << 13)) >> 7)) << 17);
      *(_BYTE *)(v4 + v1 + 5) ^= byte_187355000[(unsigned __int8)(v6 ^ BYTE1(v6) ^ BYTE2(v6) ^ BYTE3(v6))];
      v4 += 6LL;
    }
    while ( v4 < 0x4D4 );
    v12 = *(int *)(v1 + 452);
    qword_187E57E60 = v1;
    v13 = ((__int64 (__fastcall *)(__int64))sub_18072F9A0)(v12);
    v14 = qword_187E57E60;
    v15 = v13;
    qword_187E57E48 = v13;
    ((void (__fastcall *)(__int64, __int64, _QWORD))sub_180757D90)(
      v13,
      qword_187E57E38 + *(_DWORD *)(qword_187E57E60 + 448) - 6512,
      *(int *)(qword_187E57E60 + 452));
    v16 = 0;
    for ( i = 0xCD371567CB7722AAuLL; v16 < *(int *)(v14 + 452); ++v16 )
    {
      i ^= (i << 13) ^ ((i ^ (i << 13)) >> 7) ^ ((i ^ (i << 13) ^ ((i ^ (i << 13)) >> 7)) << 17);
      *(_BYTE *)(v16 + v15) ^= byte_187355000[(unsigned __int8)(i ^ BYTE1(i) ^ BYTE2(i) ^ BYTE3(i))];
    }
    v18 = ((__int64 (__fastcall *)(_QWORD, unsigned __int64))sub_18072F9A0)(*(int *)(v14 + 416), i);
    v19 = qword_187E57E60;
    v20 = v18;
    qword_187E57E50 = v18;
    ((void (__fastcall *)(__int64, __int64, _QWORD))sub_180757D90)(
      v18,
      qword_187E57E38 + *(_DWORD *)(qword_187E57E60 + 412) + 7336,
      *(int *)(qword_187E57E60 + 416));
    v21 = 0;
    for ( j = 0xCA335BE4CCB9844LL; v21 < *(int *)(v19 + 416); ++v21 )
    {
      j ^= (j << 13)
         ^ ((j ^ (unsigned __int64)(j << 13)) >> 7)
         ^ ((j ^ (j << 13) ^ ((j ^ (unsigned __int64)(j << 13)) >> 7)) << 17);
      *(_BYTE *)(v21 + v20) ^= byte_187355000[(unsigned __int8)(j ^ BYTE1(j) ^ BYTE2(j) ^ BYTE3(j))];
    }
    v23 = ((__int64 (__fastcall *)(_QWORD, __int64))sub_18072F9A0)(*(int *)(v19 + 1004), j);
    v24 = qword_187E57E60;
    v25 = v23;
    qword_187E57E70 = v23;
    ((void (__fastcall *)(__int64, __int64, _QWORD))sub_180757D90)(
      v23,
      qword_187E57E38 + *(_DWORD *)(qword_187E57E60 + 1000) - 7500,
      *(int *)(qword_187E57E60 + 1004));
    v26 = 0;
    for ( k = 0xC5306267CEF471C8uLL; v26 < *(int *)(v24 + 1004); ++v26 )
    {
      k ^= (k << 13) ^ ((k ^ (k << 13)) >> 7) ^ ((k ^ (k << 13) ^ ((k ^ (k << 13)) >> 7)) << 17);
      *(_BYTE *)(v26 + v25) ^= byte_187355000[(unsigned __int8)(k ^ BYTE1(k) ^ BYTE2(k) ^ BYTE3(k))];
    }
    v28 = ((__int64 (__fastcall *)(_QWORD, unsigned __int64))sub_18072F9A0)(*(int *)(v24 + 1232), k);
    v29 = qword_187E57E60;
    v30 = v28;
    qword_187E57E00 = v28;
    ((void (__fastcall *)(__int64, __int64, _QWORD))sub_180757D90)(
      v28,
      qword_187E57E38 + *(_DWORD *)(qword_187E57E60 + 1228) - 2268,
      *(int *)(qword_187E57E60 + 1232));
    v31 = 0;
    for ( m = 0xD2FB2F77402CAFDDuLL; v31 < *(int *)(v29 + 1232); ++v31 )
    {
      m ^= (m << 13) ^ ((m ^ (m << 13)) >> 7) ^ ((m ^ (m << 13) ^ ((m ^ (m << 13)) >> 7)) << 17);
      *(_BYTE *)(v31 + v30) ^= byte_187355000[(unsigned __int8)(m ^ BYTE1(m) ^ BYTE2(m) ^ BYTE3(m))];
    }
    v33 = ((__int64 (__fastcall *)(_QWORD, unsigned __int64))sub_18072F9A0)(*(int *)(v29 + 704), m);
    v34 = qword_187E57E60;
    v35 = v33;
    qword_187E57E20 = v33;
    ((void (__fastcall *)(__int64, __int64, _QWORD))sub_180757D90)(
      v33,
      qword_187E57E38 + *(_DWORD *)(qword_187E57E60 + 700) + 4468,
      *(int *)(qword_187E57E60 + 704));
    v36 = 0;
    for ( n = 0xDC5E21DDF0866AE3uLL; v36 < *(int *)(v34 + 704); ++v36 )
    {
      n ^= (n << 13) ^ ((n ^ (n << 13)) >> 7) ^ ((n ^ (n << 13) ^ ((n ^ (n << 13)) >> 7)) << 17);
      *(_BYTE *)(v36 + v35) ^= byte_187355000[(unsigned __int8)(n ^ BYTE1(n) ^ BYTE2(n) ^ BYTE3(n))];
    }
    v38 = ((__int64 (__fastcall *)(_QWORD, unsigned __int64))sub_18072F9A0)(*(int *)(v34 + 1016), n);
    v39 = qword_187E57E60;
    v40 = v38;
    qword_187E57E30 = v38;
    ((void (__fastcall *)(__int64, __int64, _QWORD))sub_180757D90)(
      v38,
      qword_187E57E38 + *(_DWORD *)(qword_187E57E60 + 1012) + 1040,
      *(int *)(qword_187E57E60 + 1016));
    v41 = 0;
    for ( ii = 0x1927ACB4476B3A93LL; v41 < *(int *)(v39 + 1016); ++v41 )
    {
      ii ^= (ii << 13)
          ^ ((ii ^ (unsigned __int64)(ii << 13)) >> 7)
          ^ ((ii ^ (ii << 13) ^ ((ii ^ (unsigned __int64)(ii << 13)) >> 7)) << 17);
      *(_BYTE *)(v41 + v40) ^= byte_187355000[(unsigned __int8)(ii ^ BYTE1(ii) ^ BYTE2(ii) ^ BYTE3(ii))];
    }
    v43 = ((__int64 (__fastcall *)(_QWORD, __int64))sub_18072F9A0)(*(int *)(v39 + 116), ii);
    v44 = (_DWORD *)qword_187E57E60;
    v45 = v43;
    qword_187E57E28 = v43;
    ((void (__fastcall *)(__int64, __int64, _QWORD))sub_180757D90)(
      v43,
      qword_187E57E38 + *(_DWORD *)(qword_187E57E60 + 112) - 7948,
      *(int *)(qword_187E57E60 + 116));
    v46 = 0;
    for ( jj = 0xDFAF6B0F88AF8314uLL; v46 < (int)v44[29]; ++v46 )
    {
      jj ^= (jj << 13) ^ ((jj ^ (jj << 13)) >> 7) ^ ((jj ^ (jj << 13) ^ ((jj ^ (jj << 13)) >> 7)) << 17);
      *(_BYTE *)(v46 + v45) ^= byte_187355000[(unsigned __int8)(jj ^ BYTE1(jj) ^ BYTE2(jj) ^ BYTE3(jj))];
    }
    v48 = (int)v44[54];
    dword_187E581D8 = v48;
    dword_187E581E8 = v44[27];
    dword_187E5810C = v48;
    v49 = *(_DWORD *)(qword_187E57E68 + 48);
    v50 = 1;
    if ( v49 > 255 )
    {
      v51 = 4;
      if ( v49 <= 0xFFFF )
        v51 = 2;
    }
    else
    {
      v51 = 1;
    }
    v52 = v44[96];
    if ( v52 > 255 )
    {
      v53 = 4;
      if ( v52 <= 0xFFFF )
        v53 = 2;
    }
    else
    {
      v53 = 1;
    }
    v54 = v44[9];
    if ( v54 > 255 )
    {
      v55 = 4;
      if ( v54 <= 0xFFFF )
        v55 = 2;
    }
    else
    {
      v55 = 1;
    }
    v56 = v44[198];
    if ( v56 > 255 )
    {
      v50 = 4;
      if ( v56 <= 0xFFFF )
        v50 = 2;
    }
    dword_187E57E10 = v51;
    HIDWORD(qword_187E57E14) = v55;
    dword_187E57E1C = v50;
    LODWORD(qword_187E57E14) = v53;
    qword_187E58140 = off_187E54AE8(v48, 24);
    qword_187E58120 = off_187E54AE8(*(int *)(qword_187E57E68 + 48), 8);
    qword_187E58128 = off_187E54AE8(*(int *)(qword_187E57E60 + 384), 8);
    qword_187E58118 = off_187E54AE8(*(int *)(qword_187E57E60 + 996), 8);
    sub_18069C540();
    LOBYTE(v0) = 1;
  }
  return v0;
}