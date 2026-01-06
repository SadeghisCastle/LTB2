import QtQuick
import QtQuick.Controls

Rectangle {
    id: automationSidebar
    width: 150
    height: parent.height
    color: "#313131"
    border.width: 3
    border.color: "#000000"

    Column {
        anchors.fill: parent
        spacing: 0

        // Header
        Rectangle {
            width: parent.width
            height: 50
            color: "#4d4d4d"
            border.width: 2
            border.color: "#00ffdf"

            Text {
                anchors.centerIn: parent
                text: "Automation"
                color: "#bbf6ef"
                font.pixelSize: 18
                font.family: "Courier"
                font.bold: true
            }
        }

        // Automation selection section
        Rectangle {
            width: parent.width
            height: 220
            color: "#676767"
            border.width: 2

            Column {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8

                Text {
                    width: parent.width
                    text: "Mode"
                    color: "#b9f4ed"
                    font.pixelSize: 14
                    font.family: "Courier"
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                }

                Rectangle {
                    width: parent.width
                    height: 45
                    color: automationSelector.currentIndex === 0 ? "#149700" : "#4d4d4d"
                    border.width: 2
                    border.color: automationSelector.currentIndex === 0 ? "#00ff00" : "#000000"
                    radius: 5

                    Button {
                        anchors.fill: parent
                        text: "HyperSpectral"
                        font.pixelSize: 11
                        font.family: "Courier"
                        onClicked: {
                            automationSelector.currentIndex = 0
                            AutomationManager.switchToHyperspectral()
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 45
                    color: automationSelector.currentIndex === 1 ? "#149700" : "#4d4d4d"
                    border.width: 2
                    border.color: automationSelector.currentIndex === 1 ? "#00ff00" : "#000000"
                    radius: 5

                    Button {
                        anchors.fill: parent
                        text: "Extinction"
                        font.pixelSize: 11
                        font.family: "Courier"
                        onClicked: {
                            automationSelector.currentIndex = 1
                            AutomationManager.switchToExtinction()
                        }
                    }
                }

                Rectangle {
                    width: parent.width
                    height: 45
                    color: automationSelector.currentIndex === 2 ? "#149700" : "#4d4d4d"
                    border.width: 2
                    border.color: automationSelector.currentIndex === 2 ? "#00ff00" : "#000000"
                    radius: 5

                    Button {
                        anchors.fill: parent
                        text: "SingleFluor"
                        font.pixelSize: 11
                        font.family: "Courier"
                        onClicked: {
                            automationSelector.currentIndex = 2
                            AutomationManager.switchToSingleFluor()
                        }
                    }
                }

                QtObject {
                    id: automationSelector
                    property int currentIndex: 2  // Default to SingleFluor
                }
            }
        }

        // Settings section
        Rectangle {
            width: parent.width
            height: 100
            color: "#676767"
            border.width: 2

            Column {
                anchors.fill: parent
                anchors.margins: 8
                spacing: 8

                Text {
                    width: parent.width
                    text: "Settings"
                    color: "#b9f4ed"
                    font.pixelSize: 14
                    font.family: "Courier"
                    font.bold: true
                    horizontalAlignment: Text.AlignHCenter
                }

                Rectangle {
                    width: parent.width
                    height: 35
                    color: "#ff6d00"
                    border.width: 2
                    radius: 5

                    Button {
                        anchors.fill: parent
                        text: "Configure"
                        font.pixelSize: 11
                        font.family: "Courier"
                        onClicked: {
                            // Placeholder for settings dialog
                            console.log("Settings clicked")
                        }
                    }
                }
            }
        }

        // Status indicator
        Rectangle {
            width: parent.width
            height: parent.height - 370
            color: "#313131"
            border.width: 0

            Column {
                anchors.centerIn: parent
                spacing: 5

                Rectangle {
                    width: 20
                    height: 20
                    radius: 10
                    color: "#00ff00"
                    border.width: 2
                    anchors.horizontalCenter: parent.horizontalCenter
                }

                Text {
                    text: "Ready"
                    color: "#bbf6ef"
                    font.pixelSize: 12
                    font.family: "Courier"
                    anchors.horizontalCenter: parent.horizontalCenter
                }
            }
        }
    }
}
