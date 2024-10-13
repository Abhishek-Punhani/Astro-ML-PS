# Moon Analyzer
<ul>
<li>We aim to develop a comprehensive tool for visualizing data derived from a machine learning model that classifies X-ray bursts</li>
<li>The tool will provide both a standalone application and a web-based interface to effectively analyze and interpret the model’s predictions</li>
<hr>

# Index
1. [Requirement and Deployment](#requirement-and-deployment)
2. [Features](#features)
3. [Preview](#preview)
4. [ML Model](#application-of-ml-model)
5. [ML-model limitations](#limitations-of-ml-model)

# Requirement and Deployment
<h3>Required Modules</h3>
<table>
    <thead>
        <tr>
            <th>Library Name</th>
            <th>Version</th>
        </tr>
    </thead>
    <tbody>
      <tr>
        <td>Python</td>
        <td>xx</td>
      </tr>
      <tr>
        <td>PostgresSQL</td>
        <td>xx</td>
      </tr>
      <tr>
        <td>node.js</td>
        <td>xx</td>
      </tr>
      <tr>
        <td>tailwind CSS</td>
        <td>xx</td>
      </tr>
    </tbody>
</table>

<h3>Local Installation</h3>

```
Type the commands inside
```
1.  Check version of Node.

```
node -v
```

2. If Node is not available download it for here https://nodejs.org/en/download/ for linux.
3. In the terminal clone the project.

```
git clone https://github.com/Abhishek-Punhani/Astro-ML-PS
```

4. Navigate to frontend folder

```
cd frontend
```

5. Install node modules in the client.

```
npm install
```
<b>add more steps accordingly</b>

# Features

<ul>
  <li>Interactive Visualizations of graph with different parameters</li>
  <li>Secure login sysem - <b>OTP verification</b> with TLS secured e-mails</li>
  <li>Users are allowed to <b>save projects</b> and can revisit thier analysis without wasting time</li>
  <li>Faster and Lighter with <b>Client-Side Caching</b> and load balancing via <b>Nginx</b></li>
</ul>

# Preview
<p>Below are the images showing the different graphs and features of the web app</p>
<div><img src="https://github.com/user-attachments/assets/8191cb45-7e1b-405e-8f82-02858e23c0ff"></div>

# Application of ML Model
<h3>Overview</h3>
<ol type="1">
<li>The tool processes X-ray light curves and identifies key properties of the detected bursts, such as rise time, decay time, prominence, and peak times. It utilizes clustering methods to classify bursts based on these features.</li>
<li>The tool can handle input files in various formats, including ASCII, FITS, and XLS. The classification criteria is based on rise_time, decay_time along with prominenceand the solution is designed to minimize false alarms while maximizing true positive detections.</li>
</ol>

<h3>Features</h3>
<ol type="1">
  <li>INPUT FORMAT: The tool accepts input files in multiple formats like ASCII, FITS, and XLS.</li>
  <li>PEAK DETECTION AND CLUSTERING: identify solar flares and fit them to a curve and cluster similar solar flares.</li>
  <li>OPEN SOURCE: the tool is developed using Python, leveraging libraries such as NumPy, SciPy, scikit-learn, and matplotlib for data processing and analysis.</li>
</ol>

# Limitations of ML Model
