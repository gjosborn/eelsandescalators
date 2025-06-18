import React, { useState } from "react";

type RegisterModalProps = {
    open: boolean;
    onClose: () => void;
    onRegister: (playerNames: string[]) => void;
};

const modalBackdropStyle: React.CSSProperties = {
    position: "fixed",
    top: 0,
    left: 0,
    width: "100vw",
    height: "100vh",
    background: "rgba(0,0,0,0.4)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 1000,
};

const modalContentStyle: React.CSSProperties = {
    background: "#fff",
    maxWidth: 400,
    width: "100%",
    padding: 24,
    borderRadius: 8,
    boxShadow: "0 2px 16px rgba(0,0,0,0.2)",
    position: "relative",
};

const closeButtonStyle: React.CSSProperties = {
    position: "absolute",
    top: 12,
    right: 12,
    background: "none",
    border: "none",
    fontSize: 20,
    cursor: "pointer",
    color: "#888",
};

const RegisterModal: React.FC<RegisterModalProps> = ({ open, onClose, onRegister }) => {
    const [numPlayers, setNumPlayers] = useState(2);
    const [playerNames, setPlayerNames] = useState(["", ""]);

    // Update playerNames array when numPlayers changes
    React.useEffect(() => {
        setPlayerNames((prev) => {
            const newArr = [...prev];
            while (newArr.length < numPlayers) newArr.push("");
            while (newArr.length > numPlayers) newArr.pop();
            return newArr;
        });
    }, [numPlayers]);

    const handleNameChange = (idx: number, value: string) => {
        setPlayerNames((prev) => {
            const arr = [...prev];
            arr[idx] = value;
            return arr;
        });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (playerNames.some((n) => !n.trim())) return;
        onRegister(playerNames);
        onClose();
    };

    const handleBackdropClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    if (!open) return null;
    return (
        <div style={modalBackdropStyle} onClick={handleBackdropClick}>
            <div style={modalContentStyle}>
                <button style={closeButtonStyle} onClick={onClose} aria-label="Close">&times;</button>
                <h2>Register Players</h2>
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: 12 }}>
                        <label>
                            Number of Players
                            <select
                                value={numPlayers}
                                onChange={e => setNumPlayers(Number(e.target.value))}
                                style={{ width: "100%" }}
                            >
                                {[2, 3, 4].map(n => (
                                    <option key={n} value={n}>{n}</option>
                                ))}
                            </select>
                        </label>
                    </div>
                    {playerNames.map((name, idx) => (
                        <div key={idx} style={{ marginBottom: 12 }}>
                            <label>
                                Player {idx + 1} Name
                                <input
                                    type="text"
                                    value={name}
                                    required
                                    onChange={e => handleNameChange(idx, e.target.value)}
                                    style={{ width: "100%" }}
                                />
                            </label>
                        </div>
                    ))}
                    <button type="submit" style={{ width: "100%" }}>
                        Start Game
                    </button>
                </form>
            </div>
        </div>
    );
};

export default RegisterModal;