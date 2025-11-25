import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs

Rectangle {
    id: fileSaveSelector
    width: 400
    height: 50
    color: "#313131"
    border.width: 3

    Rectangle {
        id: background
        x: 8
        y: 8
        width: 384
        height: 34
        color: "#676767"
        radius: 5
        border.width: 2

        Text {
            id: pathLabel
            x: 10
            y: 3
            color: "#b9f4ed"
            text: qsTr("Save Location:")
            font.pixelSize: 10
            font.styleName: "Bold"
            font.family: "Courier"
        }

        Rectangle {
            id: browseButtonBackground
            x: 10
            y: 16
            width: 364
            height: 18
            color: "#149700"
            border.width: 2

            Button {
                id: browseButton
                anchors.fill: parent
                text: qsTr("Browse Save Location...")
                font.pixelSize: 9
                onClicked: folderDialog.open()
            }
        }
    }

    FolderDialog {
        id: folderDialog
        title: "Select Save Location"
        currentFolder: StandardPaths.standardLocations(StandardPaths.DocumentsLocation)[0]
        
        onAccepted: {
            var path = folderDialog.selectedFolder.toString()
            // Remove file:/// prefix
            path = path.replace(/^(file:\/{2,3})/, "")
            MasterCoreBackend.setSaveLocation(path)
        }
    }
}