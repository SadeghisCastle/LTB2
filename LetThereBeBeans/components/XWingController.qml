// XWingController.qml
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 220
    height: 380
    title: qsTr("X-Wing Controller")

    Rectangle {
        id: xwingController
        width: 200
        height: 351
        anchors.centerIn: parent
        color: "#6f6f6f"
        radius: 5
        border.width: 2

        Button {
            id: moveUp
            x: 73
            y: 105
            width: 55
            height: 40
            text: qsTr("Up")
            icon.color: "#b23a3a"
            onClicked: backend.moveUp()
        }

        Button {
            id: moveDown
            x: 73
            y: 152
            width: 55
            height: 40
            text: qsTr("Down")
            onClicked: backend.moveDown()
        }

        Button {
            id: moveRight
            x: 134
            y: 152
            width: 55
            height: 40
            text: qsTr("Right")
            onClicked: backend.moveRight()
        }

        Button {
            id: moveLeft
            x: 12
            y: 152
            width: 55
            height: 40
            text: qsTr("Left")
            onClicked: backend.moveLeft()
        }

        Rectangle {
            id: rectangle1
            x: 0
            y: 0
            width: 100
            height: 80
            color: "#4d4d4d"
            border.color: "#000000"
            bottomLeftRadius: 10
            topLeftRadius: 10
            scale: 0.9

            Label {
                id: xPosition
                x: 23
                y: 20
                width: 55
                height: 40
                text: backend.xPosString
                horizontalAlignment: Text.AlignHCenter
                scale: 0.9
            }

            Text {
                id: xPositionIndicator
                x: 9
                y: 56
                color: "#ffffff"
                text: qsTr("X Position (mm)")
                font.pixelSize: 12
                scale: 0.9
            }
        }

        Rectangle {
            id: rectangle2
            x: 100
            y: 0
            width: 100
            height: 80
            color: "#4d4d4d"
            border.width: 1
            bottomRightRadius: 10
            topRightRadius: 10
            topLeftRadius: 0
            scale: 0.9

            Label {
                id: yPosition
                x: 22
                y: 20
                width: 55
                height: 40
                text: backend.yPosString
                horizontalAlignment: Text.AlignHCenter
                scale: 0.9
            }

            Text {
                id: yPositionIndicator
                x: 9
                y: 58
                color: "#ffffff"
                text: qsTr("Y Position (mm)")
                font.pixelSize: 12
                scale: 0.9
            }
        }

        Button {
            id: home
            x: 8
            y: 86
            width: 43
            height: 18
            text: qsTr("Home")
            font.pointSize: 6
            onClicked: backend.home()
        }

        Rectangle {
            id: cordinates
            x: 10
            y: 219
            width: 180
            height: 124
            color: "#4d4d4d"
            border.width: 1
            topLeftRadius: 20

            Label {
                id: yGoTo
                x: 104
                y: 17
                width: 55
                height: 40
                text: qsTr("Y")
                horizontalAlignment: Text.AlignHCenter
            }

            Label {
                id: xGoTo
                x: 21
                y: 17
                width: 55
                height: 40
                text: qsTr("X")
                horizontalAlignment: Text.AlignHCenter
            }

            TextInput {
                id: xSetPosition
                x: 8
                y: 46
                width: 80
                height: 20
                color: "#ffffff"
                text: ""
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
            }

            TextInput {
                id: ySetPosition
                x: 92
                y: 46
                width: 80
                height: 20
                color: "#ffffff"
                text: ""
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
            }

            Button {
                id: setPosition
                x: 60
                y: 84
                text: qsTr("Go!")
                onClicked: backend.setPosition(xSetPosition.text, ySetPosition.text)
            }

            Button {
                id: setHome
                x: 116
                y: 98
                width: 56
                height: 18
                text: qsTr("Set Home")
                font.pointSize: 6
                onClicked: backend.setHome()
            }

            Image {
                id: image
                x: 124
                y: -117
                width: 54
                height: 46
                source: "x-wing.png"
                rotation: 20.014
                fillMode: Image.PreserveAspectFit
            }
        }
    }
}
