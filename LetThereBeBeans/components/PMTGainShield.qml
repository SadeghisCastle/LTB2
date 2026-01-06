import QtQuick
import QtQuick.Controls

Rectangle {
    id: pmtGainShieldController
    width: 200
    height: 250
    color: "#313131"
    border.width: 3

    // Title
    Text {
        id: pmtGainShieldTitle
        x: 8
        y: 8
        width: 184
        height: 26
        color: "#bbf6ef"
        text: "PMT Gain Shield"
        font.pixelSize: 15
        font.family: "Courier"
        font.bold: true
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    // Main container
    Rectangle {
        x: 8
        y: 40
        width: 184
        height: 202
        color: "#676767"
        border.width: 2
        radius: 10

        // Current Gain Display
        Rectangle {
            id: currentGainBackground
            x: 42
            y: 20
            width: 100
            height: 35
            color: "#ffffff"
            border.width: 2

            Text {
                id: currentGainDisplay
                anchors.centerIn: parent
                text: PMTGainShieldBackend.currentGain
                font.pixelSize: 16
                font.family: "Cascadia Mono"
                color: "#000000"
                font.bold: true
            }
        }

        Label {
            id: currentGainLabel
            x: 42
            y: 60
            width: 100
            height: 20
            text: "Current Gain"
            color: "#b9f4ed"
            font.pixelSize: 12
            font.family: "Courier"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
        }

        // Spacer
        Rectangle {
            x: 42
            y: 90
            width: 100
            height: 2
            color: "#4d4d4d"
        }

        // Desired Gain Input
        Rectangle {
            id: desiredGainBackground
            x: 42
            y: 105
            width: 100
            height: 35
            color: "#ffffff"
            border.width: 2

            TextInput {
                id: desiredGainInput
                anchors.centerIn: parent
                width: 90
                text: "0.000"
                font.pixelSize: 16
                font.family: "Cascadia Mono"
                color: "#ff6d00"
                font.bold: true
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }

        Label {
            id: desiredGainLabel
            x: 42
            y: 145
            width: 100
            height: 20
            text: "Set Gain"
            color: "#b9f4ed"
            font.pixelSize: 12
            font.family: "Courier"
            font.bold: true
            horizontalAlignment: Text.AlignHCenter
        }

        // Set Button
        Rectangle {
            x: 67
            y: 172
            width: 50
            height: 25
            color: "#149700"
            border.width: 3
            radius: 5

            Button {
                id: setGainButton
                anchors.fill: parent
                text: "Set"
                font.pixelSize: 12
                font.family: "Courier"
                font.bold: true
                onClicked: PMTGainShieldBackend.setGain(desiredGainInput.text)
            }
        }
    }

    // Invisible button for title area (consistent with other components)
    Button {
        x: 8
        y: 8
        width: 184
        height: 26
        text: ""
        display: AbstractButton.IconOnly
        enabled: false
    }
}
