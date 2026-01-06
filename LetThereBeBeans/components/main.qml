import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 750
    height: 800
    title: "Hyperspectral"

    Row {
        anchors.fill: parent
        spacing: 0

        // ========================================
        // AUTOMATION SIDEBAR
        // ========================================
        Loader {
            width: 150
            height: 800
            source: "AutomationSidebar.qml"
        }

        // ========================================
        // LEFT COLUMN - Position & Hardware Controls
        // ========================================
        Column {
            width: 200
            height: 800
            spacing: 0

            Loader {
                width: 200
                height: 350
                source: "XWingController.qml"
            }

            Loader {
                width: 200
                height: 200
                source: "OscilloscopeController.qml"
            }

            Loader {
                width: 200
                height: 250
                source: "PMTGainShield.qml"
            }
        }

        // ========================================
        // RIGHT COLUMN - Spectroscopy & Automation
        // ========================================
        Column {
            width: 400
            height: 800
            spacing: 0

            Loader {
                width: 400
                height: 300
                source: "CornerstoneController.qml"
            }

            Loader {
                width: 400
                height: 350
                source: "PositionManager.qml"
            }

            // Automation Start/Stop Controls
            Rectangle {
                width: 400
                height: 150
                color: "#313131"
                border.width: 3

                Text {
                    id: automationControlsTitle
                    x: 8
                    y: 8
                    width: 384
                    height: 26
                    color: "#bbf6ef"
                    text: "Automation Controls"
                    font.pixelSize: 15
                    font.family: "Courier"
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                }

                Rectangle {
                    x: 8
                    y: 42
                    width: 384
                    height: 100
                    color: "#676767"
                    radius: 5
                    border.width: 2

                    // Start Scan Button
                    Rectangle {
                        x: 42
                        y: 20
                        width: 300
                        height: 30
                        color: "#149700"
                        border.width: 2
                        radius: 5

                        Button {
                            anchors.fill: parent
                            text: "Start Scan"
                            font.pixelSize: 14
                            font.family: "Courier"
                            font.bold: true
                            onClicked: AutomationBackend.threading()
                        }
                    }

                    // Stop Scan Button
                    Rectangle {
                        x: 42
                        y: 60
                        width: 300
                        height: 30
                        color: "#d80000"
                        border.width: 2
                        radius: 5

                        Button {
                            anchors.fill: parent
                            text: "Stop Scan"
                            font.pixelSize: 14
                            font.family: "Courier"
                            font.bold: true
                            onClicked: AutomationBackend.stopScan()
                        }
                    }
                }
            }
        }
    }
}
