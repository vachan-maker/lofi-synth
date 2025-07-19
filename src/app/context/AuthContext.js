"use client";
import React, { createContext, useState, useContext, useEffect } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isClient, setIsClient] = useState(false);

    useEffect(() => {
        setIsClient(true);
        
        try {
            const storedToken = localStorage.getItem('authToken');
            const storedUser = localStorage.getItem('userData');
            
            if (storedToken && storedUser) {
                setToken(storedToken);
                setUser(JSON.parse(storedUser));
            }
        } catch (error) {
            console.error('Error loading auth data:', error);
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
        }
        
        setLoading(false);
    }, []);

    const loginAction = async (data) => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/auth/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });

            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Server did not return JSON');
            }

            const res = await response.json();

            if (response.ok) {
                const userData = { username: data.username };
                setUser(userData);
                setToken(res.access);
                localStorage.setItem('authToken', res.access);
                localStorage.setItem('userData', JSON.stringify(userData));
                return { success: true };
            } else {
                return { success: false, error: res.error || 'Login failed' };
            }
        } catch (err) {
            console.error('Login error:', err);
            return { success: false, error: err.message || 'Network error occurred' };
        }
    };

    const logOut = () => {
        setUser(null);
        setToken(null);
        localStorage.removeItem('authToken');
        localStorage.removeItem('userData');
    };

    return (
        <AuthContext.Provider value={{ 
            token, 
            user: isClient ? user : null,
            loginAction, 
            logOut, 
            loading: loading || !isClient
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
