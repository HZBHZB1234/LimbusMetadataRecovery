// Hidden C++ exception states: #wind=15
const void *__fastcall sub_1806A2460(_BYTE *a1)
{
  void *v2; // rax
  WCHAR *v3; // rcx
  __int64 v4; // r15
  size_t v5; // rsi
  void **v6; // rdi
  void *v7; // rbx
  __int128 *p_Src; // rdx
  __int64 v9; // r8
  DWORD dwFlagsAndAttributes; // ebx
  __int128 *v11; // rdx
  __int64 v12; // r8
  const WCHAR *v13; // rcx
  WCHAR *v14; // rcx
  int v15; // edi
  WCHAR *v16; // rcx
  const WCHAR *v17; // rcx
  HANDLE FileW; // rbx
  DWORD LastError; // ebx
  WCHAR *v20; // rcx
  const char *v21; // rdx
  WCHAR *v22; // rcx
  const void *v23; // rbx
  void *v24; // rcx
  void *v25; // rcx
  __int128 Src; // [rsp+40h] [rbp-79h] BYREF
  __int64 v28; // [rsp+50h] [rbp-69h]
  unsigned __int64 v29; // [rsp+58h] [rbp-61h]
  LPCWSTR v30[2]; // [rsp+60h] [rbp-59h] BYREF
  __int64 v31; // [rsp+70h] [rbp-49h]
  unsigned __int64 v32; // [rsp+78h] [rbp-41h]
  LPCWSTR lpFileName[3]; // [rsp+80h] [rbp-39h] BYREF
  unsigned __int64 v34; // [rsp+98h] [rbp-21h]
  void *v35[3]; // [rsp+A0h] [rbp-19h] BYREF
  unsigned __int64 v36; // [rsp+B8h] [rbp-1h]
  _DWORD FileInformation[12]; // [rsp+C0h] [rbp+7h] BYREF

  v30[0] = (LPCWSTR)"Metadata";
  v30[1] = (LPCWSTR)8;
  v2 = (void *)sub_180706670(lpFileName);
  sub_1806A82B0(v35, v2);
  if ( v34 >= 0x10 )
  {
    v3 = (WCHAR *)lpFileName[0];
    if ( v34 + 1 >= 0x1000 )
    {
      if ( (unsigned __int64)lpFileName[0] - *((_QWORD *)lpFileName[0] - 1) - 8 > 0x1F )
        invalid_parameter_noinfo_noreturn();
      v3 = (WCHAR *)*((_QWORD *)lpFileName[0] - 1);
    }
    j_j_free(v3);
  }
  v4 = -1;
  v5 = -1;
  do
    ++v5;
  while ( a1[v5] );
  v6 = v35;
  if ( v36 >= 0x10 )
    v6 = (void **)v35[0];
  v7 = v35[2];
  Src = 0;
  v28 = 0;
  v29 = 15;
  LOBYTE(Src) = 0;
  sub_18069DE30(&Src);
  sub_18069E130(&Src, v6, (size_t)v7);
  sub_1806A8570(&Src, 1u);
  sub_18069E130(&Src, a1, v5);
  p_Src = &Src;
  if ( v29 >= 0x10 )
    p_Src = (__int128 *)Src;
  v9 = -1;
  do
    ++v9;
  while ( *((_BYTE *)p_Src + v9) );
  sub_1806D7230(v30);
  dwFlagsAndAttributes = 128;
  v11 = &Src;
  if ( v29 >= 0x10 )
    v11 = (__int128 *)Src;
  v12 = -1;
  do
    ++v12;
  while ( *((_BYTE *)v11 + v12) );
  sub_1806D7230(lpFileName);
  v13 = (const WCHAR *)lpFileName;
  if ( v34 >= 8 )
    v13 = lpFileName[0];
  if ( GetFileAttributesExW(v13, GetFileExInfoStandard, FileInformation) )
  {
    v15 = FileInformation[0];
    if ( v34 >= 8 )
    {
      v16 = (WCHAR *)lpFileName[0];
      if ( 2 * v34 + 2 >= 0x1000 )
      {
        if ( (unsigned __int64)lpFileName[0] - *((_QWORD *)lpFileName[0] - 1) - 8 > 0x1F )
          invalid_parameter_noinfo_noreturn();
        v16 = (WCHAR *)*((_QWORD *)lpFileName[0] - 1);
      }
      j_j_free(v16);
    }
    if ( v15 != -1 && (v15 & 0x10) != 0 )
      dwFlagsAndAttributes = 33554560;
  }
  else
  {
    GetLastError();
    if ( v34 >= 8 )
    {
      v14 = (WCHAR *)lpFileName[0];
      if ( 2 * v34 + 2 >= 0x1000 )
      {
        if ( (unsigned __int64)lpFileName[0] - *((_QWORD *)lpFileName[0] - 1) - 8 > 0x1F )
          invalid_parameter_noinfo_noreturn();
        v14 = (WCHAR *)*((_QWORD *)lpFileName[0] - 1);
      }
      j_j_free(v14);
    }
  }
  v17 = (const WCHAR *)v30;
  if ( v32 >= 8 )
    v17 = v30[0];
  FileW = CreateFileW(v17, 0x80000000, 1u, 0, 3u, dwFlagsAndAttributes, 0);
  if ( FileW == (HANDLE)-1LL )
  {
    LastError = GetLastError();
    if ( v32 >= 8 )
    {
      v20 = (WCHAR *)v30[0];
      if ( 2 * v32 + 2 >= 0x1000 )
      {
        if ( (unsigned __int64)v30[0] - *((_QWORD *)v30[0] - 1) - 8 > 0x1F )
          invalid_parameter_noinfo_noreturn();
        v20 = (WCHAR *)*((_QWORD *)v30[0] - 1);
      }
      j_j_free(v20);
    }
    v31 = 0;
    v32 = 7;
    LOWORD(v30[0]) = 0;
    if ( LastError )
    {
      v21 = (const char *)&Src;
      if ( v29 >= 0x10 )
        v21 = (const char *)Src;
      sub_1807055C0("ERROR: Could not open %s", v21);
      goto LABEL_55;
    }
  }
  else
  {
    if ( v32 >= 8 )
    {
      v22 = (WCHAR *)v30[0];
      if ( 2 * v32 + 2 >= 0x1000 )
      {
        if ( (unsigned __int64)v30[0] - *((_QWORD *)v30[0] - 1) - 8 > 0x1F )
          invalid_parameter_noinfo_noreturn();
        v22 = (WCHAR *)*((_QWORD *)v30[0] - 1);
      }
      j_j_free(v22);
    }
    v31 = 0;
    v32 = 7;
    LOWORD(v30[0]) = 0;
    v4 = (__int64)FileW;
  }
  v23 = (const void *)sub_180705640((HANDLE)v4);
  if ( !CloseHandle((HANDLE)v4) && GetLastError() )
  {
    sub_1807059D0(v23);
LABEL_55:
    v23 = 0;
  }
  if ( v29 >= 0x10 )
  {
    v24 = (void *)Src;
    if ( v29 + 1 >= 0x1000 )
    {
      if ( (unsigned __int64)(Src - *(_QWORD *)(Src - 8) - 8) > 0x1F )
        invalid_parameter_noinfo_noreturn();
      v24 = *(void **)(Src - 8);
    }
    j_j_free(v24);
  }
  v28 = 0;
  v29 = 15;
  LOBYTE(Src) = 0;
  if ( v36 >= 0x10 )
  {
    v25 = v35[0];
    if ( v36 + 1 >= 0x1000 )
    {
      if ( (unsigned __int64)v35[0] - *((_QWORD *)v35[0] - 1) - 8 > 0x1F )
        invalid_parameter_noinfo_noreturn();
      v25 = (void *)*((_QWORD *)v35[0] - 1);
    }
    j_j_free(v25);
  }
  return v23;
}
