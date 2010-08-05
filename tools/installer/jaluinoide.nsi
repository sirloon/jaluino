!include LogicLib.nsh

!define PREFIX_PATH "..\addins"
!define PRODUCT_NAME "JaluinoIDE"
!define PRODUCT_VERSION "0.2.1"
!define NSIS_PRODUCT_VERSION "${PRODUCT_VERSION}.0"
!define COMPANY_NAME "Jaluino Group"
!define UNINSTALLER_FILENAME "UninstallJaluinoIDE.exe"
!define OUT_FILE "jaluinoide-${PRODUCT_VERSION}.exe"

; 3rdparty versions
!define EDITRA_VERSION "0.5.72"
!define PYTHON_VERSION "2.6"
!define LIBUSB_VERSION "1.1.14.3"
!define PYUSB_VERSION "0.4.3"
!define PYSER_VERSION "2.5"

; The name of the installer
Name "${PRODUCT_NAME}"
; The file to write
OutFile "${OUT_FILE}"
; icon
Icon "jaluinoide.ico"
UninstallIcon "jaluinoide.ico"

; The default installation directory
InstallDir ""

; Versioning information
VIAddVersionKey "ProductName" "${PRODUCT_NAME}"
VIAddVersionKey "FileDescription" "${PRODUCT_NAME}"
VIAddVersionKey "FileVersion" "${NSIS_PRODUCT_VERSION}"
VIAddVersionKey "CompanyName" "${COMPANY_NAME}"
VIAddVersionKey "LegalCopyright" "© ${COMPANY_NAME}"
VIProductVersion "${NSIS_PRODUCT_VERSION}"


Function .onInit

	SetOutPath $TEMP
	File /oname=spltmp.bmp "jaluinoide_splash.bmp"

	splash::show 2000 $TEMP\spltmp

	Pop $0 	; $0 has '1' if the user closed the splash screen early,
			; '0' if everything closed normally, and '-1' if some error occurred.

	Delete $TEMP\spltmp.bmp

FunctionEnd
	

; Pages
Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles


Section "Install Editra ${EDITRA_VERSION}"
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR\3rdparty
  File "..\..\3rdparty\editra.win32.${EDITRA_VERSION}.exe"
  ExecWait "$INSTDIR\3rdparty\editra.win32.${EDITRA_VERSION}.exe"
  Delete "$INSTDIR\3rdparty\editra.win32.${EDITRA_VERSION}.exe"
SectionEnd ; end the section

Section "Install Python ${PYTHON_VERSION}"
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR\3rdparty  
  File "..\..\3rdparty\python-${PYTHON_VERSION}.msi"
  ExecWait '"msiexec" /i "$INSTDIR\3rdparty\python-${PYTHON_VERSION}.msi"'
  Delete "$INSTDIR\3rdparty\python-${PYTHON_VERSION}.msi"
SectionEnd ; end the section

Section "Install libusb ${LIBUSB_VERSION}"
  SetOutPath $INSTDIR\3rdparty
  File "..\..\3rdparty\libusb-win32-filter-bin-${LIBUSB_VERSION}.exe"
  ExecWait "$INSTDIR\3rdparty\libusb-win32-filter-bin-${LIBUSB_VERSION}.exe"
  Delete "$INSTDIR\3rdparty\libusb-win32-filter-bin-${LIBUSB_VERSION}.exe"
SectionEnd

Section "Install python-usb ${PYUSB_VERSION}"
  SetOutPath $INSTDIR\3rdparty
  File "..\..\3rdparty\pyusb-${PYUSB_VERSION}.win32-py${PYTHON_VERSION}.exe"
  ExecWait "$INSTDIR\3rdparty\pyusb-${PYUSB_VERSION}.win32-py${PYTHON_VERSION}.exe"
  Delete "$INSTDIR\3rdparty\pyusb-${PYUSB_VERSION}.win32-py${PYTHON_VERSION}.exe"
SectionEnd

Section "Install python-serial ${PYSER_VERSION}"
  SetOutPath $INSTDIR\3rdparty
  File "..\..\3rdparty\pyserial-${PYSER_VERSION}.win32.exe"
  ExecWait "$INSTDIR\3rdparty\pyserial-${PYSER_VERSION}.win32.exe"
  Delete "$INSTDIR\3rdparty\pyserial-${PYSER_VERSION}.win32.exe"
SectionEnd


!define PYEXE "python.exe"
Var PYDIR
Var PYPATH
DirText "Select a directory to install JaluinoIDE and jallib/jaluino libraries and samples"
Section "Install JaluinoIDE"

  SectionIn RO
  SetOutPath $INSTDIR
  File /r "..\distrib\jaluino-${PRODUCT_VERSION}\*"
  ; find pythont to run install.py and configure jaluinoide
  ReadRegStr $PYDIR HKLM "SOFTWARE\Python\PythonCore\2.6\InstallPath" ""
  IfErrors lbl_err
  Goto lbl_config
  lbl_err:
    messageBox MB_OK "Can't find python 2.6 installed, JaluinoIDE can't be configured"
    Abort
  lbl_config:
    StrCpy $PYPATH "$PYDIR${PYEXE}"
    ExecWait '$PYPATH "$INSTDIR\install.py"'
  WriteUninstaller "$INSTDIR\${UNINSTALLER_FILENAME}"
  
SectionEnd ; end the section




Section "Uninstall"
  Delete "$INSTDIR\${UNINSTALLER_FILENAME}"
SectionEnd
