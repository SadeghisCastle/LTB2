import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts
ApplicationWindow{
    visible: true
    width: 400
    height: 300
    title: qsTr("Cornerstone Controller")
    Row {
        id: cornerstoneController
        width: 400
        height: 301

        Rectangle {
            id: cornerstoneControllerPrimary
            width: 200
            height: 300
            color: "#6f6f6f"
            border.width: 2

            Button {
                id: openShutter
                x: 12
                y: 208
                text: qsTr("Open")
                onClicked: CornerstoneBackend.openShutter() 
            }

            Button {
                id: closeShutter
                x: 81
                y: 206
                text: qsTr("Close")
                onClicked: CornerstoneBackend.closeShutter()
            }

            Label {
                id: shutterStateLabel
                x: 38
                y: 230
                text: CornerstoneBackend.shutterPos
                font.pixelSize: 12
            }

            TextInput {
                id: setWavelength
                x: 40
                y: 64
                width: 80
                height: 20
                text: qsTr("Set Wavelength")
                font.pixelSize: 12
            }

            Label {
                id: currentWavelength
                x: 21
                y: 156
                text: CornerstoneBackend.wavePos
                font.pixelSize: 12
            }

            Button {
                id: goToWavelength
                x: 57
                y: 106
                text: qsTr("Go")
                onClicked: CornerstoneBackend.setWavelength(setWavelength.text)
            }

            Text {
                id: conerstoneControllerTitle
                x: 25
                y: 21
                text: qsTr("Spectrograph Controller")
                font.pixelSize: 12
            }

            Text {
                id: shutterControlLabel
                x: 38
                y: 184
                text: qsTr("Shutter controls")
                font.pixelSize: 12
            }
        }

        Rectangle {
            id: cornerstoneControllerAlt
            width: 200
            height: 300
            color: "#6f6f6f"
            border.width: 2

            ColumnLayout {
                id: columnLayout
                x: 0
                y: 0
                width: 200
                height: 150
                uniformCellSizes: false
                spacing: 0

                Rectangle {
                    id: scanController
                    width: 200
                    height: columnLayout.height
                    color: "#6f6f6f"

                    TextInput {
                        id: startWavelength
                        x: 33
                        y: 26
                        width: 80
                        height: 20
                        text: qsTr("Start")
                        font.pixelSize: 12
                    }

                    TextInput {
                        id: endWavelength
                        x: 33
                        y: 58
                        width: 80
                        height: 20
                        text: qsTr("End")
                        font.pixelSize: 12
                    }

                    TextInput {
                        id: numSteps
                        x: 33
                        y: 84
                        width: 80
                        height: 20
                        text: qsTr("Number of Steps")
                        font.pixelSize: 12
                    }

                    Button {
                        id: startScan
                        x: 77
                        y: 110
                        text: qsTr("Scan")
                    }
                }

                Rectangle {
                    id: gratingController
                    width: 200
                    height: columnLayout.height
                    color: "#6f6f6f"

                    ComboBox {
                        id: gratings
                        x: 22
                        y: 59
                        width: 157
                        height: 32
                        displayText: "1"
                        editable: false
                        model: ["1", "2", "3"]
                        // displayText will automatically be the currently selected item
                        // so you usually don't need to set displayText manually
                    }

                    Button {
                        id: changeGrating
                        x: 67
                        y: 97
                        text: qsTr("Change")
                    }

                    Text {
                        id: gratingLabel
                        x: 64
                        y: 37
                        text: qsTr("Select Grating")
                        font.pixelSize: 12
                    }
                }
            }
        }
    }
}