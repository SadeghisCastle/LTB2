import QtQuick
import QtQuick.Controls

Rectangle {
    id: pmtgainshieldController
    width: 200
    height: 160
    color: "#6f6f6f"
    radius: 5
    border.width: 2

    Rectangle {
        id: cordinates
        x: 10
        y: 10
        width: 180
        height: 150
        color: "#4d4d4d"
        border.width: 1
        topLeftRadius: 20

        Rectangle {
            id: inputTextBackground
            x: 40
            y: 10
            width: 100
            height: 20
            color: "#000000"
        }

        TextInput {
            id: inputText
            x: 40
            y: 10
            width: 100
            height: 20
            color: "#ff6d00"
            text: qsTr("0.000")
            font.pixelSize: 17
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.family: "Cascadia Mono"
        }

        Label {
            id: desiredGainLabel
            x: 70
            y: 35
            width: 100
            height: 20
            text: qsTr("Desired Gain")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.wordSpacing: -0.8
            font.family: "Cascadia Mono"
        }

        Label {
            id: gainDisplay
            x: 70
            y: 65
            width: 100
            height: 20
            text:  PMTGainShieldBackend.currentGain()
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.wordSpacing: -0.8
            font.family: "Cascadia Mono"
        }

        Label {
            id: gainDisplayLabel
            x: 70
            y: 90
            width: 100
            height: 20
            text:  qsTr("Current Gain")
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            font.wordSpacing: -0.8
            font.family: "Cascadia Mono"
        }


        Button {
            id: setGain
            x: 75
            y: 120
            width: 50
            height: 20
            text: qsTr("Set")
            font.family: "Consolas"
            onClicked: PMTGainShieldBackend.setGain(inputText.text)
            background: Rectangle {
                id: buttonBackground
                x: 0
                y: 0
                width: 50
                height: 20
                color: "#017a03"
                radius: 0
                border.width: 2
                bottomRightRadius: 0
                topRightRadius: 27
                bottomLeftRadius: 7
                topLeftRadius: 0
            }
        }
      

    }

}
