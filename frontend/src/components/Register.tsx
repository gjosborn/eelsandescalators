import React, { useState } from "react";

type AuthResponse = {
    access_token: string;
    token_type: string;
    user_id: number;
};

type AuthMode = "register" | "login";

type RegisterModalProps = {
    open: boolean;
    onClose: () => void;
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

const RegisterModal: React.FC<RegisterModalProps> = ({ open, onClose }) => {
    const [mode, setMode] = useState<AuthMode>("register");
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [displayName, setDisplayName] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState<string | null>(null);

    if (!open) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setSuccess(null);
        setLoading(true);

        try {
            let response: Response;
            if (mode === "register") {
                response = await fetch("/auth/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        username,
                        email,
                        password,
                        display_name: displayName || undefined,
                    }),
                });
            } else {
                response = await fetch("/auth/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password }),
                });
            }

            if (!response.ok) {
                const data = await response.json();
                setError(data.detail || "Authentication failed");
            } else {
                const data: AuthResponse = await response.json();
                setSuccess("Success! You are now logged in.");
                // Store token as needed, e.g., localStorage.setItem("token", data.access_token)
            }
        } catch (err) {
            setError("Network error");
        } finally {
            setLoading(false);
        }
    };

    const handleBackdropClick = (e: React.MouseEvent) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    return (
        <div style={modalBackdropStyle} onClick={handleBackdropClick}>
            <div style={modalContentStyle}>
                <button style={closeButtonStyle} onClick={onClose} aria-label="Close">&times;</button>
                <h2>{mode === "register" ? "Register" : "Login"}</h2>
                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: 12 }}>
                        <label>
                            Username
                            <input
                                type="text"
                                value={username}
                                required
                                onChange={e => setUsername(e.target.value)}
                                style={{ width: "100%" }}
                            />
                        </label>
                    </div>
                    {mode === "register" && (
                        <>
                            <div style={{ marginBottom: 12 }}>
                                <label>
                                    Email
                                    <input
                                        type="email"
                                        value={email}
                                        required
                                        onChange={e => setEmail(e.target.value)}
                                        style={{ width: "100%" }}
                                    />
                                </label>
                            </div>
                            <div style={{ marginBottom: 12 }}>
                                <label>
                                    Display Name (optional)
                                    <input
                                        type="text"
                                        value={displayName}
                                        onChange={e => setDisplayName(e.target.value)}
                                        style={{ width: "100%" }}
                                    />
                                </label>
                            </div>
                        </>
                    )}
                    <div style={{ marginBottom: 12 }}>
                        <label>
                            Password
                            <input
                                type="password"
                                value={password}
                                required
                                onChange={e => setPassword(e.target.value)}
                                style={{ width: "100%" }}
                            />
                        </label>
                    </div>
                    {error && <div style={{ color: "red", marginBottom: 12 }}>{error}</div>}
                    {success && <div style={{ color: "green", marginBottom: 12 }}>{success}</div>}
                    <button type="submit" disabled={loading} style={{ width: "100%" }}>
                        {loading ? "Please wait..." : mode === "register" ? "Register" : "Login"}
                    </button>
                </form>
                <div style={{ marginTop: 16, textAlign: "center" }}>
                    {mode === "register" ? (
                        <span>
                            Already have an account?{" "}
                            <button
                                type="button"
                                onClick={() => setMode("login")}
                                style={{ background: "none", border: "none", color: "#007bff", cursor: "pointer" }}
                            >
                                Login
                            </button>
                        </span>
                    ) : (
                        <span>
                            Need an account?{" "}
                            <button
                                type="button"
                                onClick={() => setMode("register")}
                                style={{ background: "none", border: "none", color: "#007bff", cursor: "pointer" }}
                            >
                                Register
                            </button>
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RegisterModal;