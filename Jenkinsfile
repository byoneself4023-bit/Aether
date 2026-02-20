pipeline {
    agent any

    environment {
        DOCKER_REGISTRY  = credentials('docker-registry-url')   // e.g. ghcr.io/your-org
        DOCKER_CREDS     = credentials('docker-registry-creds') // username:token
        DEPLOY_HOST      = credentials('deploy-ssh-host')       // e.g. user@10.0.0.1
        DEPLOY_SSH_KEY   = credentials('deploy-ssh-key')
        GEMINI_API_KEY   = credentials('gemini-api-key')
        POSTGRES_PASSWORD = credentials('postgres-password')
        JWT_SECRET       = credentials('jwt-secret')
        IMAGE_TAG        = "${env.BUILD_NUMBER}-${env.GIT_COMMIT?.take(7) ?: 'unknown'}"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    stages {
        // =====================================================
        // 1. Checkout
        // =====================================================
        stage('Checkout') {
            steps {
                checkout scm
                sh 'echo "Branch: ${GIT_BRANCH}, Commit: ${GIT_COMMIT}"'
            }
        }

        // =====================================================
        // 2. Test Backend (병렬)
        // =====================================================
        stage('Test Backend') {
            parallel {
                stage('portfolio-service') {
                    steps {
                        dir('portfolio-service') {
                            sh '''
                                python -m venv .venv
                                . .venv/bin/activate
                                pip install -q -r requirements.txt
                                python -m pytest tests/ -x -q \
                                    --junitxml=../reports/portfolio-test-results.xml
                            '''
                        }
                    }
                }

                stage('llm-service') {
                    steps {
                        dir('llm-service') {
                            sh '''
                                python -m venv .venv
                                . .venv/bin/activate
                                pip install -q -r requirements.txt
                                python -m pytest tests/ -x -q \
                                    --junitxml=../reports/llm-test-results.xml
                            '''
                        }
                    }
                }

                stage('auth-service') {
                    steps {
                        dir('auth-service') {
                            sh '''
                                chmod +x gradlew
                                ./gradlew test --no-daemon \
                                    -Dspring.profiles.active=test
                            '''
                        }
                    }
                }
            }
        }

        // =====================================================
        // 3. Test Frontend
        // =====================================================
        stage('Test Frontend') {
            steps {
                dir('frontend') {
                    sh '''
                        npm ci --prefer-offline
                        npm run build
                    '''
                }
            }
        }

        // =====================================================
        // 4. Docker Build
        // =====================================================
        stage('Docker Build') {
            steps {
                sh """
                    docker compose build
                """

                // 빌드된 이미지에 태그 부여 (compose 서비스명 기준)
                sh """
                    docker tag aether-portfolio-service ${DOCKER_REGISTRY}/aether-portfolio:${IMAGE_TAG}
                    docker tag aether-llm-service       ${DOCKER_REGISTRY}/aether-llm:${IMAGE_TAG}
                    docker tag aether-auth-service      ${DOCKER_REGISTRY}/aether-auth:${IMAGE_TAG}
                    docker tag aether-frontend          ${DOCKER_REGISTRY}/aether-frontend:${IMAGE_TAG}

                    docker tag aether-portfolio-service ${DOCKER_REGISTRY}/aether-portfolio:latest
                    docker tag aether-llm-service       ${DOCKER_REGISTRY}/aether-llm:latest
                    docker tag aether-auth-service      ${DOCKER_REGISTRY}/aether-auth:latest
                    docker tag aether-frontend          ${DOCKER_REGISTRY}/aether-frontend:latest
                """
            }
        }

        // =====================================================
        // 5. Docker Push
        // =====================================================
        stage('Docker Push') {
            when {
                branch 'main'
            }
            steps {
                sh """
                    echo ${DOCKER_CREDS_PSW} | docker login ${DOCKER_REGISTRY} \
                        -u ${DOCKER_CREDS_USR} --password-stdin
                """

                sh """
                    docker push ${DOCKER_REGISTRY}/aether-portfolio:${IMAGE_TAG}
                    docker push ${DOCKER_REGISTRY}/aether-llm:${IMAGE_TAG}
                    docker push ${DOCKER_REGISTRY}/aether-auth:${IMAGE_TAG}
                    docker push ${DOCKER_REGISTRY}/aether-frontend:${IMAGE_TAG}

                    docker push ${DOCKER_REGISTRY}/aether-portfolio:latest
                    docker push ${DOCKER_REGISTRY}/aether-llm:latest
                    docker push ${DOCKER_REGISTRY}/aether-auth:latest
                    docker push ${DOCKER_REGISTRY}/aether-frontend:latest
                """
            }
        }

        // =====================================================
        // 6. Deploy
        // =====================================================
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sshagent(credentials: ['deploy-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${DEPLOY_HOST} << 'DEPLOY_SCRIPT'
                            cd /opt/aether
                            export IMAGE_TAG=${IMAGE_TAG}
                            export DOCKER_REGISTRY=${DOCKER_REGISTRY}

                            docker compose pull
                            docker compose up -d --remove-orphans

                            echo "Waiting for health checks..."
                            sleep 30

                            # 헬스체크 확인
                            curl -sf http://localhost:8001/health || exit 1
                            curl -sf http://localhost:8002/health || exit 1
                            curl -sf http://localhost:8003/actuator/health || exit 1
                            curl -sf http://localhost:3000 || exit 1

                            echo "Deploy complete: ${IMAGE_TAG}"
DEPLOY_SCRIPT
                    """
                }
            }
        }
    }

    // =========================================================
    // Post Actions
    // =========================================================
    post {
        always {
            // 테스트 리포트 수집
            junit(
                testResults: 'reports/*-test-results.xml',
                allowEmptyResults: true
            )
            junit(
                testResults: 'auth-service/build/test-results/test/*.xml',
                allowEmptyResults: true
            )

            // Workspace 정리
            cleanWs(deleteDirs: true, patterns: [
                [pattern: '**/.venv/**', type: 'INCLUDE'],
                [pattern: '**/node_modules/**', type: 'INCLUDE'],
                [pattern: '**/build/**', type: 'INCLUDE'],
            ])
        }

        success {
            echo "Pipeline succeeded: Build #${env.BUILD_NUMBER}"
            // Slack webhook URL 설정 후 활성화
            // slackSend(channel: '#aether-deploy', color: 'good',
            //     message: "Aether 배포 성공: Build #${env.BUILD_NUMBER} (${env.GIT_BRANCH})")
        }

        failure {
            echo "Pipeline failed: Build #${env.BUILD_NUMBER}"
            // Slack webhook URL 설정 후 활성화
            // slackSend(channel: '#aether-deploy', color: 'danger',
            //     message: "Aether 빌드 실패: Build #${env.BUILD_NUMBER} (${env.GIT_BRANCH})\n${env.BUILD_URL}")
        }
    }
}
