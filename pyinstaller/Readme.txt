Pythonスクリプトの利用が難しい方向けに、
Pyinstallerを使って実行ファイル(Win/Mac向け)を生成する方法メモ

【経緯】
FMVプロジェクトで発生したFW1.6.0でのインシデントを受け、
Firmware ConfigによってFirmware Versionを固定する運用に変更予定。
update_firmware_config_from_list.pyをベースに、
コマンドラインの操作が不要な
update_firmware_config_for_fmv.py
を作成し、pyinstallerで実行ファイル化する。
運用想定者がWin/Macの両方あるため、それぞれの端末上でコンパイルして配布する

【pipenvを使って仮想環境を作成】
インストールが必要なライブラリは以下の通り
・requests
・tortilla

【pyinstallerで実行ファイル作成】
pyinstaller [スクリプト] --onefile

※参考にしたサイト
https://camp.trainocate.co.jp/magazine/pyinstaller-python-exe/