#!/bin/bash

INSTALL_DIR="$HOME/.local/share/madescha"
BIN_DIR="$HOME/.local/bin"

# Create venv
python3 -m venv "$INSTALL_DIR/venv"

# Install package into venv
"$INSTALL_DIR/venv/bin/pip" install .

# Create wrapper script
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/madescha" << EOF
#!/bin/bash
exec "$INSTALL_DIR/venv/bin/madescha" "\$@"
EOF

chmod +x "$BIN_DIR/madescha"

# Install desktop file and icon
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons
cp data/madescha.desktop ~/.local/share/applications/
cp data/madescha_icon_128x128.png ~/.local/share/icons/
update-desktop-database ~/.local/share/applications


# Make sure BIN_DIR is in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    if ! grep -q "$BIN_DIR" ~/.bashrc 2>/dev/null; then
        #echo "export PATH=\"$BIN_DIR:\$PATH\"" >> ~/.profile
        echo "export PATH=\"$BIN_DIR:\$PATH\"" >> ~/.bashrc
        echo "Added $BIN_DIR to PATH in ~/.bashrc"
    fi
    echo "Note: Re-login or run 'source ~/.bashrc' for PATH to take effect"
fi

echo "Installed successfully"