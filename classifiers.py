import numpy as np
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Example: EMG data should be a matrix of size (n_samples, n_features)
# Labels should be a vector of size (n_samples,)
# Generate synthetic data for illustration purposes
n_samples = 100
n_features = 10
n_classes = 3

# Simulate feature matrix (replace with actual EMG feature data)
X = np.random.rand(n_samples, n_features)
y = np.random.randint(n_classes, size=n_samples)

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Create and train the LDA model
lda = LinearDiscriminantAnalysis()
lda.fit(X_train, y_train)

# Predict on the test set
y_pred = lda.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f'Classification Accuracy: {accuracy:.2f}')



def sample_train_data(classes, samples_per_class, n_features):
    X = np.zeros((len(classes) * samples_per_class, n_features))
    for i_class in classes:
        X