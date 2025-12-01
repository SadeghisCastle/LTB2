import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: oscilloscopeController
    width: 200
    height: 150
    color: "#313131"
    border.width: 3

    Rectangle {
        id: background
        x: 8
        y: 8
        width: 184
        height: 134
        color: "#676767"
        radius: 10
        border.width: 3

        Text {
            id: title
            x: 35
            y: 10
            color: "#bbf6ef"
            text: qsTr("Oscilloscope")
            font.pixelSize: 16
            font.styleName: "Bold"
            font.family: "Courier"
        }

        Rectangle {
            id: startLiveButton
            x: 17
            y: 40
            width: 150
            height: 25
            color: "#149700"
            border.width: 2

            Button {
                id: startLive
                anchors.fill: parent
                text: qsTr("Start Live View")
                font.pixelSize: 10
                onClicked: OscilloscopeBackend.startLiveView()
            }
        }

        Rectangle {
            id: stopLiveButton
            x: 17
            y: 70
            width: 150
            height: 25
            color: "#d80000"
            border.width: 2

            Button {
                id: stopLive
                anchors.fill: parent
                text: qsTr("Stop Live View")
                font.pixelSize: 10
                onClicked: OscilloscopeBackend.stopLiveView()
            }
        }

        Rectangle {
            id: singleCaptureButton
            x: 17
            y: 100
            width: 150
            height: 25
            color: "#2196F3"
            border.width: 2

            Button {
                id: singleCapture
                anchors.fill: parent
                text: qsTr("Single Capture")
                font.pixelSize: 10
                onClicked: OscilloscopeBackend.captureSingle()
            }
        }
    }
}