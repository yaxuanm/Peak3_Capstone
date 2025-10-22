# AWS Deployment Guide for Peak3 Backend

## 🎯 Goal
Deploy Python backend to AWS EC2 so Forge frontend can call it from the cloud.

## 📋 Step-by-Step Process

### 1. AWS EC2 Setup
- Launch EC2 instance (t2.micro - free tier)
- Configure security groups (allow HTTP/HTTPS)
- Install Python and dependencies

### 2. Backend Deployment
- Upload Python code to EC2
- Install requirements
- Configure environment variables
- Start the Flask server

### 3. Forge Integration
- Update Forge config with AWS public IP
- Deploy Forge app
- Test integration

## 💰 Cost Estimate
- EC2 t2.micro: FREE (12 months)
- Data transfer: ~$1-5/month
- Total: Almost FREE

## 🚀 Ready to start?
Let's begin with EC2 instance creation!



