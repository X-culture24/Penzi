# Use official Node.js image
FROM node:20

# Set the working directory
WORKDIR /app

# Copy package files first for caching
COPY package.json package-lock.json ./

# Install React dependencies
RUN npm install

# Copy all frontend files
COPY . .

# Expose React development port
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]

